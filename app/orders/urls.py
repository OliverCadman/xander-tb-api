"""URL Routing for Orders API"""

from django.urls import path
from orders.views import OrderCreateView

app_name = "orders"

urlpatterns = [
    path('create_full_order', OrderCreateView.as_view(),
         name='create_full_order')
]
