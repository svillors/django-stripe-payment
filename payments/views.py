from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

import stripe

from .models import Item


stripe.api_key = settings.STRIPE_SECRET_KEY


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    return render(request, 'item_detail.html', {
        'item': item,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    })


def buy_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': item.currency,
                    'product_data': {
                        'name': item.name,
                        'description': item.description,
                    },
                    'unit_amount': int(item.price_in_cents),
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        success_url=f'{settings.DOMAIN}/success/',
        cancel_url=f'{settings.DOMAIN}/cancel/',
    )

    return JsonResponse({
        'session_id': session.id,
    })
