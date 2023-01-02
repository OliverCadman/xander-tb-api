"""
Data models for 3 different toothbrush order types
All 3 models inherit from parent 'AbstractTBData' class.
"""

from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser,
                                        PermissionsMixin)

from django.core.validators import MaxValueValidator


class UserManager(BaseUserManager):
    """Manager for user models"""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""

        if not email:
            raise ValueError(
                'Please enter an email address.'
            )

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):

        user = self.create_user(
            email, password
        )

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Model to represent user in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = UserManager()

class DeliveryPostcode(models.Model):
    """
    Model to represent a Delivery Postcode.

    Attributes:
        postcode (str): The postcode itself.
        postcode_type (int):
            1. Delivery
            2. Billing
        todays_order (TodaysOrder): A reference to a TodaysOrder model
        full_order (FullOrder): A reference to a FullOrder model (null to start)

    """

    postcode = models.CharField(max_length=20)
    postcode_area = models.CharField(max_length=5, null=True)
    country = models.CharField(max_length=30, null=True)
    latitude = models.DecimalField(decimal_places=8, max_digits=15, null=True)
    longitude = models.DecimalField(decimal_places=8, max_digits=15, null=True)

    def __str__(self):
        return self.postcode


class BillingPostcode(models.Model):
    """
    Model to represent a Billing Postcode.

    Attributes:
        postcode (str): The postcode itself.
        postcode_type (int):
            1. Delivery
            2. Billing
        todays_order (TodaysOrder): A reference to a TodaysOrder model
        full_order (FullOrder): A reference to a FullOrder model (null to start)

    """

    postcode = models.CharField(max_length=20)
    postcode_area = models.CharField(max_length=5, null=True)
    country = models.CharField(max_length=30, null=True)
    latitude = models.DecimalField(decimal_places=8, max_digits=15, null=True)
    longitude = models.DecimalField(decimal_places=8, max_digits=15, null=True)


    def __str__(self):
        return self.postcode


class AbstractTBData(models.Model):
    """
    Parent model to inherit from.
    """

    class Meta:
        abstract = True

    order_number = models.CharField(max_length=30, null=False, unique=True)
    toothbrush_type = models.CharField(max_length=20)
    order_date = models.DateTimeField()
    customer_age = models.IntegerField()
    order_quantity = models.IntegerField()
    is_first = models.BooleanField()
    dispatch_status = models.CharField(max_length=30, null=False, blank=False)
    dispatch_date = models.DateTimeField()
    delivery_status = models.CharField(max_length=30, null=False, blank=False)
    delivery_date = models.DateTimeField()


class FullOrder(AbstractTBData):

    delivery_postcode = models.OneToOneField(
        DeliveryPostcode, on_delete=models.CASCADE, related_name='full_delivery_pc', null=True)
    billing_postcode = models.OneToOneField(
        BillingPostcode, on_delete=models.CASCADE, related_name='full_billing_pc', null=True)

    def __str__(self):
        return self.order_number
    
    @property
    def toothbrush_count(self):
        count = self.toothbrush_type.count
        return count



class TodaysOrder(AbstractTBData):

    dispatch_status = models.CharField(max_length=30, null=True, blank=True)
    dispatch_date = models.DateTimeField(null=True, blank=True)
    delivery_status = models.CharField(max_length=30, null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)

    delivery_postcode = models.OneToOneField(
        DeliveryPostcode, on_delete=models.CASCADE, related_name='today_delivery_pc', null=True)
    billing_postcode = models.OneToOneField(
        BillingPostcode, on_delete=models.CASCADE, related_name='today_billing_pc', null=True)

    def __str__(self):
        return self.order_number


class NullOrder(AbstractTBData):

    dispatch_status = models.CharField(max_length=30, null=True, blank=True)
    dispatch_date = models.DateTimeField(null=True, blank=True)
    delivery_status = models.CharField(max_length=30, null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)

    delivery_postcode = models.OneToOneField(
        DeliveryPostcode, on_delete=models.CASCADE, related_name='null_delivery_pc', null=True)
    billing_postcode = models.OneToOneField(
        BillingPostcode, on_delete=models.CASCADE, related_name='null_billing_pc', null=True)

    def __str__(self):
        return self.order_number
