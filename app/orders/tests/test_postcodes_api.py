"""Test for Postcode API Operations."""

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    FullOrder,
    TodaysOrder,
    NullOrder,
    DeliveryPostcode,
    BillingPostcode
)

from orders.serializers import (
    FullOrderSerializer,
    NullOrderSerializer,
    TodaysOrderSerializer,
    DeliveryPostcodeSerializer,
    BillingPostcodeSerializer
)

import datetime
import pytz

DELIVERY_POSTCODE_URL = reverse('orders:delivery_postcodes-list')
BILLING_POSTCODE_URL = reverse('orders:billing_postcodes-list')


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


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


class PublicPostcodeAPITests(TestCase):
    """Unit testing for Postcode API."""

    def setUp(self):
        self.client = APIClient()

    def test_postcodes_POST(self):
        """
        Test submitting a POST request to create billing
        and delivery postcodes.
        """

        test_todays_order = TodaysOrder.objects.create(
            order_number='Test Order Number',
            order_date=time_now,
            toothbrush_type='Test Toothbrush',
            order_quantity=10,
            customer_age=50,
            is_first=True,
        )

        test_delivery_postcode = 'Delivery Postcode'
        test_billing_postcode = 'Billing Postcode'

        delivery_postcode_payload = {
            'postcode': test_delivery_postcode,
            'todays_order': test_todays_order.id
        }

        billing_postcode_payload = {
            'postcode': test_billing_postcode,
            'todays_order': test_todays_order.id
        }

        delivery_res = self.client.post(
            DELIVERY_POSTCODE_URL,
            delivery_postcode_payload,
            format='json'
        )

        billing_res = self.client.post(
            BILLING_POSTCODE_URL,
            billing_postcode_payload,
            format='json'
        )

        print('DELIVERY RES CONTENT:', delivery_res.content)

        self.assertEqual(delivery_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(billing_res.status_code, status.HTTP_201_CREATED)

        delivery_postcode = DeliveryPostcode.objects.get(postcode='Delivery Postcode')
        billing_postcode = BillingPostcode.objects.get(postcode='Billing Postcode')

        print('DELIVERY POSTCODE:', delivery_postcode)
        print('BILLING POSTCODE:', billing_postcode)

        test_todays_order.refresh_from_db()

        delivery_serializer = DeliveryPostcodeSerializer(delivery_postcode)
        billing_serializer = BillingPostcodeSerializer(billing_postcode)

        print('DELIVERY RES?:', delivery_res.data)

        self.assertEqual(delivery_res.data, delivery_serializer.data)
        self.assertEqual(billing_res.data, billing_serializer.data)
