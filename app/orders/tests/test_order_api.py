"""Tests for the order API."""

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from orders.serializers import (FullOrderSerializer, NullOrderSerializer,
                                TodaysOrderSerializer)

import pytz
import datetime
from time import perf_counter

import json

from core.models import FullOrder, NullOrder, TodaysOrder


def detail_url(order_type, order_id, filtered=None):
    """Create and return a recipe detail URL."""

    if not filtered:
        return reverse(f'orders:{order_type}-detail', args=[order_id])
    
    return reverse(f'orders:{order_type}-detail', kwargs={'pk': order_id, 'filtered': True})


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))

# Define URL endpoints
# GET_ORDER_URL = reverse('orders:get')


FULL_ORDER_URL = reverse('orders:full_orders-list')
TODAYS_ORDER_URL = reverse('orders:todays_orders-list')
NULL_ORDER_URL = reverse('orders:null_orders-list')

# Helper variable
time_now = pytz.utc.localize(datetime.datetime.now())

json_time = json_serial(pytz.utc.localize(datetime.datetime.now()))


def create_order(type_order, **params):
    """Creates either a FUll Order, Null Order or Todays Order"""

    defaults = {
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

    defaults.update(params)

    order = None

    if type_order == 'Full Order':
        order = FullOrder.objects.create(**defaults)
    elif type_order == 'Todays Order':
        order = TodaysOrder.objects.create(**defaults)
    else:
        order = NullOrder.objects.create(**defaults)

    return order


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

        self.order_number2 = 'BRU00002'

    def test_create_order_success(self):
        """Test creating an order is successful"""

        res = self.client.post(FULL_ORDER_URL, self.payload)
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

        res = self.client.post(FULL_ORDER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_full_order_creation_with_list_serializer(self):
        """Test the performance of a bulk full-order creation"""

        TEST_SIZE = 3

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
            FULL_ORDER_URL,
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
            TODAYS_ORDER_URL,
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
            TODAYS_ORDER_URL,
            self.payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_todays_bulk_order_creation(self):
        """
        Test bulk creation of todays orders
        """

        TEST_SIZE = 3000

        t1 = perf_counter()

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
            TODAYS_ORDER_URL,
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
        TEST_SIZE = 3

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
            NULL_ORDER_URL,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(res.json()), TEST_SIZE)

        t2 = perf_counter()

        print(f"Null order bulk creation took {t2 - t1} seconds to complete.")

    def test_get_full_orders(self):
        """Test retrieving a list of full orders."""

        create_order('Full Order')
        create_order('Full Order', order_number=self.order_number2)

        res = self.client.get(FULL_ORDER_URL)

        all_full_orders = FullOrder.objects.all()
        serializer = FullOrderSerializer(all_full_orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_null_orders(self):
        """Test retrieving a list of null orders."""

        create_order('Null Order')
        create_order('Null Order', order_number=self.order_number2,
                     dispatch_status=None)

        res = self.client.get(NULL_ORDER_URL)

        all_null_orders = NullOrder.objects.all()
        serializer = NullOrderSerializer(all_null_orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_todays_orders(self):
        """Test retrieving a list of todays orders."""

        create_order('Todays Order')
        create_order('Todays Order', order_number=self.order_number2,
                     dispatch_status=None)

        res = self.client.get(TODAYS_ORDER_URL)

        all_todays_orders = TodaysOrder.objects.all()
        serializer = TodaysOrderSerializer(all_todays_orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_full_order_insertion_with_json_loads(self):

        self.payload['order_date'] = json_time
        self.payload['dispatch_date'] = json_time
        self.payload['delivery_date'] = json_time
        json_data = json.dumps(self.payload)

        res = self.client.post(FULL_ORDER_URL, json.loads(json_data))
    
    def test_get_null_orders(self):
        """Test getting only null orders from DB"""

        # Objects with complete data
        for x in range(1, 10):
            TodaysOrder.objects.create(
                order_number=f'BRU00000{x}',
                order_date=json_time,
                toothbrush_type='Test Toothbrush',
                customer_age=20,
                order_quantity=5,
                delivery_postcode='Test Postcode',
                billing_postcode='Test Postcode',
                is_first=True,
                dispatch_status='Test Dispatch Status',
                dispatch_date=json_time,
                delivery_status='Test Delivery Status',
                delivery_date=json_time
            )
    
        # Objects with null data
        for x in range(10, 20):
            TodaysOrder.objects.create(
                order_number=f'BRU00000{x}',
                order_date=json_time,
                toothbrush_type='Test Toothbrush',
                customer_age=20,
                order_quantity=5,
                delivery_postcode='Test Postcode',
                billing_postcode='Test Postcode',
                is_first=True,
                dispatch_status='Test Dispatch Status',
                dispatch_date=None,
                delivery_status=None,
                delivery_date=None
            )
        

        url = reverse('orders:todays_orders-list')

        res = self.client.get(url, data={'filter_by_null': True}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        queryset = TodaysOrder.objects.filter(delivery_status=None)

        serializer = TodaysOrderSerializer(queryset, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_bulk_order_update(self):
        """Test bulk update of orders."""

        COMPLETE_ORDER_SIZE = 10
        NULL_ORDER_SIZE = 10

        complete_orders = []
        null_orders = []

        for x in range(1, 10):
            complete_orders.append(
                TodaysOrder.objects.create(
                    order_number=f'BRU00000{x}',
                    order_date=json_time,
                    customer_age=20,
                    order_quantity=5,
                    delivery_postcode='Test Postcode',
                    billing_postcode='Test Postcode',
                    is_first=True,
                    dispatch_status='Test Dispatch Status',
                    dispatch_date=json_time,
                    delivery_status='Test Delivery Status',
                    delivery_date=json_time
                )
            )
        
        for x in range(10, 20):
            null_orders.append(
                TodaysOrder.objects.create(
                    order_number=f'BRU00000{x}',
                    order_date=json_time,
                    customer_age=20,
                    order_quantity=5,
                    delivery_postcode='Test Postcode',
                    billing_postcode='Test Postcode',
                    is_first=True,
                    dispatch_status='Test Dispatch Status',
                    dispatch_date=None,
                    delivery_status=None,
                    delivery_date=None
                )
            )

        get_null_orders_url = reverse('orders:todays_orders-list')
        todaysorders_queryset = self.client.get(get_null_orders_url, data={
            'filter_by_null': True
        })

        todaysorders_data = todaysorders_queryset.data

        for d in todaysorders_data:
            for k, v in d.items():
                if k == 'id':
                    test_url = detail_url(
                        'todays_orders',
                        v
                    )

                    payload = {
                        'dispatch_date': json_time,
                        'delivery_status': 'TEST PATCH DELIVERY STATUS',
                        'delivery_date': json_time,
                        'dispatch_status': 'TEST PATCH DISPATCH STATUS'
                    }

                    res = self.client.patch(
                        test_url,
                        data=json.dumps(payload),
                        content_type='application/json',
                        
                    )
        
                    self.assertEqual(res.status_code, status.HTTP_200_OK)

        no_null_queryset = TodaysOrder.objects.filter(
            dispatch_date=None, delivery_status=None, delivery_date=None)
        
        self.assertEqual(len(no_null_queryset), 0)