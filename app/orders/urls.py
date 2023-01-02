"""URL Routing for Orders API"""

from django.urls import path, include
from orders.views import (
    FullOrderViewSet,
    TodaysOrderViewSet,
    NullOrderViewSet,
    CountToothbrushTypesViewSet,
    DeliveryPostcodeViewSet,
    BillingPostcodeViewset
)

from rest_framework.routers import DefaultRouter


app_name = "orders"

router = DefaultRouter(trailing_slash=False)
router.register('full_orders', FullOrderViewSet, basename='full_orders')
router.register('todays_orders', TodaysOrderViewSet, basename='todays_orders')
router.register('null_orders', NullOrderViewSet, basename='null_orders'),
router.register('delivery_postcodes', DeliveryPostcodeViewSet, basename='delivery_postcodes')
router.register('billing_postcodes', BillingPostcodeViewset, basename='billing_postcodes')

urlpatterns = [
    path('', include(router.urls)),
    path('count_tb_type', CountToothbrushTypesViewSet.as_view({'get': 'list'}), name='count_tb_type')
]
