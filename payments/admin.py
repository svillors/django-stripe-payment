from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import Item, Order, OrderItem


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'currency')


class OrderItemInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        currencies = set()

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue

            if form.cleaned_data.get('DELETE'):
                continue

            item = form.cleaned_data.get('item')
            if item is None:
                continue

            currencies.add(item.currency)

        if len(currencies) > 1:
            raise ValidationError('All items in order must have the same currency')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    formset = OrderItemInlineFormSet
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderItemInline,)
    list_display = ('id', 'created_at')
