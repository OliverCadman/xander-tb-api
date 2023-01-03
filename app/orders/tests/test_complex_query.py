'''Test Order API, complex querying.'''

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import FullOrder
from orders.serializers import FullOrderSerializer

from numpy import random

import datetime
import json

import pytz


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class ComplexAPIQueryTests(TestCase):
    '''Unit testing for complex querying of Order models.'''

    def setUp(self):
        self.client = APIClient()
        self.json_time = json_serial(pytz.utc.localize(datetime.datetime.today()))

        TEST_SIZE = 20

        self.payload = [{
            'order_number': f'BRU0000{x}',
            'toothbrush_type': f'Test Toothbrush {random.choice(3, 4)}000',
            'order_date': self.json_time,
            'customer_age': 25,
            'order_quantity': 10,
            'delivery_postcode': 'Test Delivery Postcode',
            'billing_postcode': 'Test Billing Postcode',
            'is_first': True,
            'dispatch_status': 'Test Dispatch Status',
            'dispatch_date': self.json_time,
            'delivery_status': 'Test Delivery Status',
            'delivery_date': 'Test Delivery Date',
        }
        for x in range(TEST_SIZE)
        ]

    

    def test_get_amount_of_toothbrushes_sold(self):
        
        print(self.payload)