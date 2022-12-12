"""
Data models for 3 different toothbrush order types
All 3 models inherit from parent 'AbstractTBData' class.
"""

from django.db import models


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