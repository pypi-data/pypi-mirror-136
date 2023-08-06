from django.db import models
from django.conf import settings
from .validators import positive_number
from .fields import UniqueBooleanField


class ActionType(models.Model):
    """Model of the types of actions performed with the product."""

    name = models.CharField(max_length=255, verbose_name='Name')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'type'
        verbose_name_plural = 'Actions'


class Category(models.Model):
    """Product category model."""

    name = models.CharField(max_length=255, verbose_name='Name')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'Categories'


class Unit(models.Model):
    """Unit model."""

    name = models.CharField(max_length=20, verbose_name='Name')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'unit'
        verbose_name_plural = 'Units'


class AbstractProduct(models.Model):
    """Abstract model for Product models."""

    name = models.CharField(max_length=255, verbose_name='Name')
    barcode = models.CharField(max_length=255, null=True, blank=True, verbose_name='Barcode')
    qrcode = models.CharField(max_length=500, null=True, blank=True, verbose_name='QR-code')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.PROTECT, verbose_name='Category')
    product_count = models.FloatField(validators=[positive_number], verbose_name='Count')
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name='Unit')
    weight = models.FloatField(validators=[positive_number], verbose_name='Weight')
    purchase_price = models.FloatField(validators=[positive_number], verbose_name='Purchase price')
    price = models.FloatField(validators=[positive_number], verbose_name='Price')
    promotion_price = models.FloatField(validators=[positive_number], null=True, blank=True,
                                        verbose_name='Promotional price')
    promotion_product = models.BooleanField(default=False, verbose_name='Promotional product')
    image = models.ImageField(upload_to='static/images/', null=True, blank=True, verbose_name='Image')
    active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        abstract = True


class Product(AbstractProduct):
    """The product model is inherited from the 'AbstractProduct' abstract model.
    When you perform actions on the model, you interact with the 'ProductHistory' model."""

    def add_history(self, action_type, exists):
        """Adding history."""

        ProductHistory.objects.create(
            product=self,
            action=action_type,
            name=self.name,
            barcode=self.barcode,
            qrcode=self.qrcode,
            category=self.category,
            product_count=self.product_count,
            unit=self.unit,
            weight=self.weight,
            purchase_price=self.purchase_price,
            price=self.price,
            promotion_price=self.promotion_price,
            image=self.image,
            active=self.active,
            exists=exists,
        )

        carts = CartList.objects.all()
        for cart in carts:
            cart.save()

    def addition_or_change_history(self, curt_number=None, *args, **kwargs):
        """Adding history on 'save'/'update' of the Product model."""

        if not self.pk:
            action_type = ActionType.objects.filter(name='Product addition').first()
        else:
            if curt_number:
                action_type = ActionType.objects.filter(name='Sale of products').first()
            else:
                action_type = ActionType.objects.filter(name='Product change').first()

        super().save(*args, **kwargs)

        return action_type

    def unexists_history(self):
        """Adding history on 'delete' of the Product model."""

        action_type = ActionType.objects.filter(name='Product removal').first()
        self.add_history(action_type, False)
        ProductHistory.objects.filter(product=self).update(exists=False)

    def save(self, cart_number=None, *args, **kwargs):
        """Redefined 'create'/'update' function. It then adds an entry to the 'ProductHistory' model."""

        action_type = self.addition_or_change_history(cart_number)
        self.add_history(action_type, True)

    def delete(self, *args, **kwargs):
        """Redefined 'delete' function. It then adds an entry to the 'ProductHistory' model."""

        self.unexists_history()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f'[{self.pk}] {self.name}'

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'Products'


class CartList(models.Model):
    """Cart model."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, limit_choices_to={'is_staff': True, 'is_active': True},
                             on_delete=models.PROTECT, verbose_name='Cashier')
    last_update = models.DateTimeField(auto_now=True, verbose_name='Last update')

    def __str__(self):
        full_name = self.user.get_full_name()

        if full_name:
            full_name = f' / {self.user.get_full_name()}'

        return f'[{self.pk}] {self.user}{full_name}'

    class Meta:
        verbose_name = 'cart action'
        verbose_name_plural = 'Cart list'


class Cart(models.Model):
    """Open cart model."""

    cart_number = models.ForeignKey(CartList, on_delete=models.CASCADE, verbose_name='Cart number')
    product = models.ForeignKey(Product, limit_choices_to={'active': True}, on_delete=models.PROTECT,
                                verbose_name='Product')
    product_count = models.FloatField(validators=[positive_number], verbose_name='Count')

    def product_count_plus(self, *args, **kwargs):
        """Adding +1 to product cart."""

        self.product_count += 1
        super().save(*args, **kwargs)

    def product_count_minus(self, *args, **kwargs):
        """Removing -1 from cart."""

        self.product_count -= 1
        super().save(*args, **kwargs)

    def sell(self, *args, **kwargs):
        """sale of products."""

        self.product.product_count -= self.product_count
        self.product.save(cart_number=True)
        cart = self.cart_number.pk
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Redefined 'create'/'update' function. It then updates the 'last_update' in the 'CartList' model."""

        super().save(*args, **kwargs)
        self.cart_number.save()

    def delete(self,  *args, **kwargs):
        """Redefined 'delete' function. It then updates the 'last_update' in the 'CartList' model."""

        super().delete(*args, **kwargs)
        self.cart_number.save()

    def __str__(self):
        return f'{self.product.price} / {self.product.name}'

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'Open carts'


class ProductHistory(models.Model):
    """Product history model."""

    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, verbose_name='Product')
    action = models.ForeignKey(ActionType, null=True, on_delete=models.PROTECT, verbose_name='Action')
    name = models.CharField(max_length=255, verbose_name='Name')
    barcode = models.CharField(max_length=255, null=True, blank=True, verbose_name='Barcode')
    qrcode = models.CharField(max_length=500, null=True, blank=True, verbose_name='QR-code')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.PROTECT, default=None,
                                 verbose_name='Category')
    product_count = models.FloatField(validators=[positive_number], verbose_name='Count')
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name='Unit')
    weight = models.FloatField(validators=[positive_number], verbose_name='Weight')
    purchase_price = models.FloatField(validators=[positive_number], verbose_name='Purchase price')
    price = models.FloatField(validators=[positive_number], verbose_name='Price')
    promotion_price = models.FloatField(validators=[positive_number], null=True, blank=True,
                                        verbose_name='Promotional price')
    promotion_product = models.BooleanField(default=False, verbose_name='Promotional product')
    image = models.ImageField(null=True, blank=True, verbose_name='Image')
    active = models.BooleanField(verbose_name='Active')
    exists = models.BooleanField(verbose_name='Available')
    action_date = models.DateTimeField(auto_now=True, verbose_name='Date')

    def __str__(self):
        return f'{self.product.name}'

    class Meta:
        verbose_name = 'history'
        verbose_name_plural = 'History'


class Currency(models.Model):
    """Currency model."""

    value = models.CharField(max_length=3, verbose_name='Currency')
    float_right = models.BooleanField(default=False, verbose_name='Fload right')
    active = UniqueBooleanField(default=True, verbose_name='Active')

    def save(self, *args, **kwargs):
        """Redefined 'create'/'update' function. It then updates the 'last_update' in the 'CartList' model."""

        super().save(*args, **kwargs)
        carts = CartList.objects.all()
        for cart in carts:
            cart.save()

    def delete(self, *args, **kwargs):
        """Redefined 'delete' function. It then updates the 'last_update' in the 'CartList' model."""

        super().delete(*args, **kwargs)
        carts = CartList.objects.all()
        for cart in carts:
            cart.save()

    def __str__(self):
        return f'{self.value}'

    class Meta:
        verbose_name = 'currency'
        verbose_name_plural = 'Currencies'
