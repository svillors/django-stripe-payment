from django.http import HttpResponse
from django.urls import path

from .views import buy_item, buy_order, item_detail, order_detail, main_page

urlpatterns = [
    path('', main_page, name='main_page'),
    path('item/<int:item_id>/', item_detail, name='item_detail'),
    path('buy/<int:item_id>/', buy_item, name='buy_item'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('buy_order/<int:order_id>/', buy_order, name='buy_order'),
    path('success/', lambda _: HttpResponse("Payment success")),
    path('cancel/', lambda _: HttpResponse("Payment canceled")),
]
