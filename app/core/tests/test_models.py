"""Unit tests for User and Toothbrush Order Data Models"""

from django.test import TestCase
from django.contrib.auth import get_user_model
import datetime
from pytz import utc

from core.models import (FullOrder, TodaysOrder, NullOrder,
                         DeliveryPostcode, BillingPostcode)

class UserModelTests(TestCase):
    """Test User Model"""

    def test_create_user_model_with_email_successful(self):
        """Test creating a user model with email address is successful"""

        email = 'testuser@test.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_users_email_normalized(self):
        """Test that a new user's email is normalized."""

        email_addresses = [
            ['test1@EXAMPLE.COM', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['Test3@ExAmPlE.COm', 'Test3@example.com'],
            ['test4@example.com', 'test4@example.com']
        ]

        for email, expected in email_addresses:
            user = get_user_model().objects.create_user(
                email=email,
                password='testpass123'
            )

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises an error."""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='testpass123'
            )

    def test_create_superuser_is_successful(self):
        """Test creating a superuser"""

        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123'
        )

        self.assertTrue(user.is_superuser)


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

    def test_create_full_orderl(self):
        """Test creating a full order."""

        full_order = FullOrder.objects.create(
            **self.order_details
        )

        self.assertEqual(full_order.__str__(),
                         self.order_details['order_number'])
    
    def test_create_todays_order(self):
        """Test creating today's order."""

        todays_order = TodaysOrder.objects.create(
            **self.order_details
        )

        self.assertEqual(todays_order.__str__(),
                         self.order_details['order_number'])

    def test_create_null_order(self):
        """Test creating a null order."""

        del self.order_details['dispatch_date']
        del self.order_details['dispatch_status']
        del self.order_details['delivery_date']
        del self.order_details['delivery_status']

        null_order = NullOrder.objects.create(
            **self.order_details
        )

        self.assertEqual(null_order.__str__(),
                         self.order_details['order_number'])
    
    def test_create_delivery_postcode_with_todays_order_relation(self):
        """Test creating a postcode object."""

        del self.order_details['dispatch_date']
        del self.order_details['dispatch_status']
        del self.order_details['delivery_date']
        del self.order_details['delivery_status']

        test_todays_order = TodaysOrder.objects.create(
            **self.order_details
        )

        postcode = 'Test Postcode'

        test_postcode = DeliveryPostcode.objects.create(
            postcode=postcode,
            todays_order=test_todays_order,
        )

        self.assertEqual(test_postcode.__str__(), postcode)

        test_todays_order.refresh_from_db()

        self.assertEqual(
            test_todays_order.delivery_postcode.__str__(),
            postcode
        )

    def test_create_billing_postcode_with_todays_order_relation(self):
        """Test creating a postcode object."""

        del self.order_details['dispatch_date']
        del self.order_details['dispatch_status']
        del self.order_details['delivery_date']
        del self.order_details['delivery_status']

        test_todays_order = TodaysOrder.objects.create(
            **self.order_details
        )

        postcode = 'Test Postcode'

        test_postcode = BillingPostcode.objects.create(
            postcode=postcode,
            todays_order=test_todays_order,
        )

        self.assertEqual(test_postcode.__str__(), postcode)   

        test_todays_order.refresh_from_db()

        self.assertEqual(
            test_todays_order.billing_postcode.__str__(),
            postcode)
    
    def test_create_delivery_postcode_with_all_object_relation(self):
        """
        Test creating a Delivery postcode with FullOrder, TodaysOrder,
        and NullOrder as related objects. 
        """

        postcode = 'Test Postcode'

        test_full_order = FullOrder.objects.create(
            **self.order_details
        )

        del self.order_details['dispatch_date']
        del self.order_details['dispatch_status']
        del self.order_details['delivery_date']
        del self.order_details['delivery_status']

        self.order_details['order_number'] = 'BRU00005678'

        test_todays_order = TodaysOrder.objects.create(**self.order_details)

        self.order_details['order_number'] = 'BRU0001234'

        test_null_order = NullOrder.objects.create(**self.order_details)

        test_postcode = DeliveryPostcode.objects.create(
            postcode=postcode,
            full_order=test_full_order,
            todays_order=test_todays_order,
            null_order=test_null_order
        )

        self.assertEqual(test_postcode.__str__(), postcode)

        test_full_order.refresh_from_db()
        test_todays_order.refresh_from_db()
        test_null_order.refresh_from_db()

        
        self.assertEqual(test_full_order.delivery_postcode.__str__(), test_postcode.__str__())
        self.assertEqual(test_null_order.delivery_postcode.__str__(), test_postcode.__str__())
        self.assertEqual(test_todays_order.delivery_postcode.__str__(), test_postcode.__str__())

    def test_create_delivery_postcode_with_all_object_relation(self):
        """
        Test creating a Billing postcode with FullOrder, TodaysOrder,
        and NullOrder as related objects. 
        """

        postcode = 'Test Postcode'

        test_full_order = FullOrder.objects.create(
            **self.order_details
        )

        del self.order_details['dispatch_date']
        del self.order_details['dispatch_status']
        del self.order_details['delivery_date']
        del self.order_details['delivery_status']

        self.order_details['order_number'] = 'BRU00005678'

        test_todays_order = TodaysOrder.objects.create(**self.order_details)

        self.order_details['order_number'] = 'BRU0001234'

        test_null_order = NullOrder.objects.create(**self.order_details)

        test_postcode = BillingPostcode.objects.create(
            postcode=postcode,
            full_order=test_full_order,
            todays_order=test_todays_order,
            null_order=test_null_order
        )

        self.assertEqual(test_postcode.__str__(), postcode)

        test_full_order.refresh_from_db()
        test_todays_order.refresh_from_db()
        test_null_order.refresh_from_db()

        
        self.assertEqual(test_full_order.billing_postcode.__str__(), test_postcode.__str__())
        self.assertEqual(test_null_order.billing_postcode.__str__(), test_postcode.__str__())
        self.assertEqual(test_todays_order.billing_postcode.__str__(), test_postcode.__str__())
