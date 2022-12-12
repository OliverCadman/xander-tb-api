"""
Data models for 3 different toothbrush order types
All 3 models inherit from parent 'AbstractTBData' class.
"""

from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser,
                                        PermissionsMixin)



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
        """Create and return a new superuser"""
        user = self.create_user(
            email, password
        )

        user.is_staff = True
        user.is_superuser = True
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
    delivery_postcode = models.CharField(max_length=20)
    billing_postcode = models.CharField(max_length=20)
    is_first = models.BooleanField()
    dispatch_status = models.CharField(max_length=30, null=False, blank=False)
    dispatch_date = models.DateTimeField()
    delivery_status = models.CharField(max_length=30, null=False, blank=False)
    delivery_date = models.DateTimeField()



class FullOrder(AbstractTBData):

    def __str__(self):
        return self.order_number



class TodaysOrder(AbstractTBData):

    def __str__(self):
        return self.order_number


class NullOrder(AbstractTBData):

    dispatch_status = models.CharField(max_length=30, null=True, blank=True)
    dispatch_date = models.DateTimeField(null=True, blank=True)
    delivery_status = models.CharField(max_length=30, null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.order_number