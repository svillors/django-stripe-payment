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
