from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

import stripe

from .models import Item, Order


stripe.api_key = settings.STRIPE_SECRET_KEY


def build_line_item(item, quantity=1):
    return {
        'price_data': {
            'currency': item.currency,
            'product_data': {
                'name': item.name,
                'description': item.description,
            },
            'unit_amount': int(item.price_in_cents),
        },
        'quantity': quantity,
    }


@require_GET
def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    return render(request, 'item_detail.html', {
        'item': item,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    })


@require_GET
def buy_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[build_line_item(item)],
        mode='payment',
        success_url=f'{settings.DOMAIN}/success/',
        cancel_url=f'{settings.DOMAIN}/cancel/',
    )

    return JsonResponse({
        'session_id': session.id,
    })


@require_GET
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order_items = list(order.items.select_related('item'))
    currencies = {order_item.item.currency for order_item in order_items}

    order_error = None
    order_currency = None

    if not order_items:
        order_error = 'Order must contain at least one item.'
    elif len(currencies) > 1:
        order_error = 'All items in order must have the same currency.'
    else:
        order_currency = currencies.pop()

    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items,
        'order_currency': order_currency,
        'order_error': order_error,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    })


@require_GET
def buy_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order_items = list(order.items.select_related('item').order_by('id'))

    line_items = [
        build_line_item(order_item.item, order_item.quantity)
        for order_item in order_items
    ]

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=f'{settings.DOMAIN}/success/',
        cancel_url=f'{settings.DOMAIN}/cancel/',
    )

    return JsonResponse({
        'session_id': session.id,
    })
