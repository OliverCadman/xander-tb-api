"""URL Routing for Orders API"""

from django.urls import path
from orders.views import (FullOrderCreateView,
                          TodaysOrderCreateView,
                          NullOrderCreateView)

app_name = "orders"

urlpatterns = [
    path('create_full_order', FullOrderCreateView.as_view(),
         name='create_full_order'),
    path('create_todays_order', TodaysOrderCreateView.as_view(),
         name='create_todays_order'),
    path('create_null_order', NullOrderCreateView.as_view(),
         name='create_null_order')
]
