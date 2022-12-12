"""Unit tests for Toothbrush Order Data Models"""

from django.test import TestCase
import datetime
from pytz import utc

from core.models import FullOrder


class ToothbrushOrderModelTests(TestCase):
    """
    Test Class for Toothbrush Order Model Creation Tests
    """

    def setUp(self):
        self.order_details = {
            'order_number': 'BRU00001234',
            'toothbrush_type': 'Test Toothbrush',
            'order_date': utc.localize(datetime.datetime.now()),
            'customer_age': 20,
            'order_quantity': 5,
            'delivery_postcode': 'Test Postcode',
            'billing_postcode': 'Test Postcode',
            'is_first': True,
            'dispatch_status': 'Test Dispatch Status',
            'dispatch_date': utc.localize(datetime.datetime.now()),
            'delivery_status': 'Test Delivery Status',
            'delivery_date': utc.localize(datetime.datetime.now())
        }
        

    def test_create_full_order_model(self):
        """Tests creating a full order."""

        full_order = FullOrder.objects.create(
            **self.order_details
        )

        self.assertEqual(full_order.__str__(), self.order_details['order_number'])
    
    def test_create_full_order_with_null_value_raises_error(self):

        del self.order_details['dispatch_status']

        print(self.order_details)

        full_order_2 = FullOrder.objects.create(
        order_number = 'BRU00001234',
        order_date = utc.localize(datetime.datetime.now()),
        customer_age = 20,
        order_quantity = 5,
        is_first = True,
        dispatch_date = utc.localize(datetime.datetime.now()),
        delivery_date = utc.localize(datetime.datetime.now())
        )
        print("FULL ORDER 2", full_order_2.dispatch_status)