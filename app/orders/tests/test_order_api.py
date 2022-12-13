"""Tests for the order API."""

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

import pytz
import datetime
from time import perf_counter

from core.models import FullOrder

import json

# Define URL endpoints
# GET_ORDER_URL = reverse('orders:get')

CREATE_FULL_ORDER_URL = reverse('orders:create_full_order')
CREATE_TODAYS_ORDER_URL = reverse('orders:create_todays_order')
CREATE_NULL_ORDER_URL = reverse('orders:create_null_order')

# Helper variable
time_now = pytz.utc.localize(datetime.datetime.now())


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class PublicOrderAPITests(TestCase):
    """Test public features of Order API"""

    def setUp(self):
        self.client = APIClient()

        self.payload = {
            "order_number": "BRU00001",
            "toothbrush_type": "Test Toothbrush",
            "order_date": time_now,
            "customer_age": 20,
            "order_quantity": 5,
            "delivery_postcode": "Test Postcode",
            "billing_postcode": "Test Postcode",
            "is_first": True,
            "dispatch_status": "Test Dispatch Status",
            "dispatch_date": time_now,
            "delivery_status": "Test Delivery Status",
            "delivery_date": time_now
        }

    def test_create_order_success(self):
        """Test creating an order is successful"""

        res = self.client.post(CREATE_FULL_ORDER_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        order = FullOrder.objects.get(
            order_number=self.payload['order_number'])
        self.assertEqual(order.order_number, self.payload['order_number'])

    def test_create_full_order_with_invalid_data_raises_error(self):
        """
        Test 400 error thrown when attempting to create
        full order with null value
        """
        self.payload['dispatch_status'] = ''

        res = self.client.post(CREATE_FULL_ORDER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_full_order_creation_with_list_serializer(self):
        """Test the performance of a bulk full-order creation"""

        TEST_SIZE = 3000

        t1 = perf_counter()

        json_time = json_serial(pytz.utc.localize(datetime.datetime.now()))

        data = [
            {
                "order_number": f"BRU0000{x}",
                "toothbrush_type": "Test Toothbrush",
                "order_date": json_time,
                "customer_age": 20,
                "order_quantity": 5,
                "delivery_postcode": "Test Postcode",
                "billing_postcode": "Test Postcode",
                "is_first": True,
                "dispatch_status": "Test Dispatch Status",
                "dispatch_date": json_time,
                "delivery_status": "Test Delivery Status",
                "delivery_date": json_time
            }
            for x in range(TEST_SIZE)
        ]

        res = self.client.post(
            CREATE_FULL_ORDER_URL,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(res.json()), TEST_SIZE)

        t2 = perf_counter()
        print(f'Optimized task took {t2 - t1} seconds to complete.')

    def test_todays_order_creation(self):
        """Test posting to create_todays_order endpoint is successful"""
        res = self.client.post(
            CREATE_TODAYS_ORDER_URL,
            self.payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_todays_order_creation_with_null_values_is_successful(self):
        """
        Test that posting to today's-order-create endpoint with null values:
            dispatch_status,
            dispatch_date,
            delivery_status,
            delivery_date

        is successful.
        """

        fields_to_make_null = ["dispatch_status", "delivery_status",
                               "dispatch_date", "delivery_date"]

        for i in list(self.payload.keys()):
            if i in fields_to_make_null:
                del self.payload[i]

        res = self.client.post(
            CREATE_TODAYS_ORDER_URL,
            self.payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_todays_bulk_order_creation(self):
        """
        Test bulk creation of todays orders
        """

        TEST_SIZE = 3000

        t1 = perf_counter()

        json_time = json_serial(pytz.utc.localize(datetime.datetime.now()))

        data = [
            {
                "order_number": f"BRU0000{x}",
                "toothbrush_type": "Test Toothbrush",
                "order_date": json_time,
                "customer_age": 20,
                "order_quantity": 5,
                "delivery_postcode": "Test Postcode",
                "billing_postcode": "Test Postcode",
                "is_first": True,
                "dispatch_status": "Test Dispatch Status",
                "dispatch_date": json_time,
                "delivery_status": "Test Delivery Status",
                "delivery_date": json_time
            }
            for x in range(TEST_SIZE)
        ]

        res = self.client.post(
            CREATE_TODAYS_ORDER_URL,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(res.json()), TEST_SIZE)

        t2 = perf_counter()

        print(f"Todays order bulk creation took {t2 - t1}"
              "seconds to complete.")

    def test_null_bulk_order_creation(self):
        """
        Test bulk creation of null orders
        """
        TEST_SIZE = 3000

        t1 = perf_counter()

        json_time = json_serial(pytz.utc.localize(datetime.datetime.now()))

        data = [
            {
                "order_number": f"BRU0000{x}",
                "toothbrush_type": "Test Toothbrush",
                "order_date": json_time,
                "customer_age": 20,
                "order_quantity": 5,
                "delivery_postcode": "Test Postcode",
                "billing_postcode": "Test Postcode",
                "is_first": True
            }
            for x in range(TEST_SIZE)
        ]

        res = self.client.post(
            CREATE_NULL_ORDER_URL,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(res.json()), TEST_SIZE)

        t2 = perf_counter()

        print(f"Null order bulk creation took {t2 - t1} seconds to complete.")
