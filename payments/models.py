from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Currency(models.TextChoices):
    USD = 'usd', 'USD'
    EUR = 'eur', 'EUR'


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


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id}'

    @property
    def total_price(self):
        return sum(
            (order_item.total_price for order_item in self.items.select_related('item')),
            Decimal('0.00'),
        )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.item} x {self.quantity}'

    @property
    def total_price(self):
        return self.item.price * self.quantity
