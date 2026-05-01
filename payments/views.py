from django.conf import settings
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

import stripe

from .models import Item, Order


stripe.api_key = settings.STRIPE_SECRET_KEY


@require_GET
def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    return render(request, 'item_detail.html', {
        'item': item,
    })


@require_GET
def checkout_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    return render(request, 'item_checkout.html', {
        'item': item,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    })


@require_GET
def buy_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(item.price_in_cents),
            currency=item.currency.lower(),
            payment_method_types=['card'],
            metadata={
                'item_id': str(item.id),
                'item_name': item.name,
                'customer_name': request.GET.get('name', ''),
                'customer_email': request.GET.get('email', ''),
                'customer_country': request.GET.get('country', ''),
            },
        )

        return JsonResponse({
            'client_secret': intent.client_secret,
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
        }, status=400)


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
    })


@require_GET
def checkout_order(request, order_id):
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

    return render(request, 'order_checkout.html', {
        'order': order,
        'order_items': order_items,
        'order_currency': order_currency,
        'order_error': order_error,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    })


@require_GET
def buy_order(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related('discount', 'tax'),
        pk=order_id
    )
    order_items = list(order.items.select_related('item').order_by('id'))

    currencies = {order_item.item.currency for order_item in order_items}

    if not order_items:
        return JsonResponse({'error': 'Order must contain at least one item.'}, status=400)

    if len(currencies) > 1:
        return JsonResponse({
            'error': 'All items in order must have the same currency.',
        }, status=400)

    order_currency = currencies.pop()

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_price * 100),
            currency=order_currency.lower(),
            payment_method_types=['card'],
            metadata={
                'order_id': str(order.id),
                'customer_name': request.GET.get('name', ''),
                'customer_email': request.GET.get('email', ''),
                'customer_country': request.GET.get('country', ''),
                'subtotal': str(order.subtotal),
                'discount_amount': str(order.discount_amount),
                'tax_amount': str(order.tax_amount),
            },
        )

        return JsonResponse({
            'client_secret': intent.client_secret,
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
        }, status=400)


@require_GET
def main_page(request):
    items = Item.objects.all()
    orders = Order.objects.annotate(items_count=Count('items'))

    return render(request, 'index.html', {
        'items': items,
        'orders': orders,
    })
