from decimal import Decimal, ROUND_HALF_UP

from django.core.validators import MinValueValidator
from django.db import models


class Currency(models.TextChoices):
    USD = 'usd', 'USD'
    EUR = 'eur', 'EUR'


class DiscountType(models.TextChoices):
    PERCENTAGE = 'percentage', 'Percentage'
    FIXED_AMOUNT = 'fixed_amount', 'Fixed amount'


class Item(models.Model):
    name = models.CharField('Name', max_length=100)
    description = models.TextField('Description', blank=True)
    price = models.DecimalField('Price', max_digits=10, decimal_places=2)
    currency = models.CharField(
        'Currency',
        max_length=3,
        choices=Currency.choices,
        default=Currency.USD,
    )

    def __str__(self):
        return self.name

    @property
    def price_in_cents(self):
        return int(self.price * 100)


class Discount(models.Model):
    name = models.CharField("Name", max_length=100)
    type = models.CharField(
        "Type of discount",
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE,
    )
    value = models.DecimalField(
        "Value",
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return self.name


class Tax(models.Model):
    name = models.CharField("Name", max_length=100)
    percentage = models.DecimalField(
        "Percentage",
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return self.name


class Order(models.Model):
    discount = models.ForeignKey(
        Discount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    tax = models.ForeignKey(
        Tax,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id}'

    @property
    def subtotal(self):
        return sum(
            (order_item.total_price for order_item in self.items.select_related('item')),
            Decimal('0.00'),
        ).quantize(Decimal('0.01'))

    @property
    def discount_amount(self):
        if not self.discount:
            return Decimal('0.00')

        if self.discount.type == DiscountType.PERCENTAGE:
            amount = self.subtotal * self.discount.value / Decimal('100')
        else:
            amount = self.discount.value

        return min(amount, self.subtotal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def tax_amount(self):
        if not self.tax:
            return Decimal('0.00')

        taxable_amount = self.subtotal - self.discount_amount
        amount = taxable_amount * self.tax.percentage / Decimal('100')

        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def total_price(self):
        return self.subtotal - self.discount_amount + self.tax_amount

    @property
    def currency(self):
        currencies = set(self.items.values_list('item__currency', flat=True))

        if len(currencies) == 1:
            return currencies.pop()

        return ''


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.item} x {self.quantity}'

    @property
    def total_price(self):
        return self.item.price * self.quantity
