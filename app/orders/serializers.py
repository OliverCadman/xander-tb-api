"""Serializers for the Orders API View."""

from rest_framework import serializers
from core.models import (FullOrder, TodaysOrder, NullOrder,
                         DeliveryPostcode, BillingPostcode)

from django.db import IntegrityError
from django.core.exceptions import ValidationError

from django.db.models import Avg

import datetime


class DeliveryPostcodeSerializer(serializers.ModelSerializer):
    """
    Serializer for Delivery Postcodes.
    """
    class Meta:
        model = DeliveryPostcode
        fields = ['id', 'postcode', 'country', 'postcode_area',
                  'longitude', 'latitude']
        read_only_fields = ['id']


class BillingPostcodeSerializer(serializers.ModelSerializer):
    """
    Serializer for Billing Postcodes.
    """
    class Meta:
        model = BillingPostcode
        fields = ['id', 'postcode', 'country', 'postcode_area',
                'longitude', 'latitude']
        read_only_fields = ['id']


class BulkCreateOrderSerializer(serializers.ListSerializer):
    """
    List Serializer for creating objects in bulk.
    """

    def create(self, validated_data):
        res = [self.child.create(attrs) for attrs in validated_data]

        try:
            self.child.Meta.model.objects.bulk_create(res)
        except IntegrityError as e:
            raise ValidationError(e)

        return res


class FullOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Full Orders.
    """

    billing_postcode = BillingPostcodeSerializer(required=False)
    delivery_postcode = DeliveryPostcodeSerializer(required=False)
    avg_customer_age = serializers.ReadOnlyField()

    class Meta:
        model = FullOrder
        fields = ['id', 'order_number', 'order_date', 'customer_age', 'order_quantity', 'toothbrush_type',
                  'delivery_postcode', 'billing_postcode', 'is_first', 'dispatch_status',
                  'dispatch_date', 'delivery_status', 'delivery_date', 'avg_customer_age']
        read_only_fields = ['id', 'avg_customer_age']
        list_serializer_class = BulkCreateOrderSerializer
    

    def create(self, validated_data):

        delivery_postcode = validated_data.pop('delivery_postcode', {})
        billing_postcode = validated_data.pop('billing_postcode', {})

        instance = FullOrder(**validated_data)
        self._get_or_create_delivery_postcode(delivery_postcode, instance)
        self._get_or_create_billing_postcode(billing_postcode, instance)

        if isinstance(self._kwargs['data'], dict):
            instance.save()

        return instance
    
    def _get_or_create_billing_postcode(self, postcode, order):

        billing_postcode = BillingPostcode.objects.create(
            **postcode
        )

        order.billing_postcode = billing_postcode
    
    def _get_or_create_delivery_postcode(self, postcode, order):

        delivery_postcode = DeliveryPostcode.objects.create(
            **postcode
        )

        order.delivery_postcode = delivery_postcode
    
    # def get_avg_customer_age(self, obj):
    #     return FullOrder.objects.all().aggregate(
    #         Avg('customer_age')
    #     )
    

class TodaysOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Todays Orders.
    """

    delivery_postcode = DeliveryPostcodeSerializer(required=False)
    billing_postcode = BillingPostcodeSerializer(required=False)

    class Meta:
        model = TodaysOrder
        fields = ['id', 'order_number', 'order_date', 'customer_age', 'order_quantity', 'toothbrush_type',
                  'delivery_postcode', 'billing_postcode', 'is_first', 'dispatch_status',
                  'dispatch_date', 'delivery_status', 'delivery_date']
        read_only_fields = ('id',)
        list_serializer_class = BulkCreateOrderSerializer

    def create(self, validated_data):
   
        delivery_postcode = validated_data.pop('delivery_postcode', {})
        billing_postcode = validated_data.pop('billing_postcode', {})

        instance = TodaysOrder(**validated_data)
        # self._get_or_create_billing_postcode(billing_postcode, instance)
        # self._get_or_create_delivery_postcode(delivery_postcode, instance)

        if isinstance(self._kwargs['data'], dict):
            instance.save()

        return instance
    
    def _get_or_create_billing_postcode(self, postcode, order):

        billing_postcode = BillingPostcode.objects.create(
            **postcode
        )

        order.billing_postcode = billing_postcode
    
    def _get_or_create_delivery_postcode(self, postcode, order):

        delivery_postcode = DeliveryPostcode.objects.create(
            **postcode
        )

        order.delivery_postcode = delivery_postcode


    def update(self, instance, validated_data):

        instance.dispatch_status = validated_data['dispatch_status']
        instance.dispatch_date = validated_data['dispatch_date']
        instance.delivery_status = validated_data['delivery_status']
        instance.delivery_date = validated_data['delivery_date']

        instance.save()
        return instance


class NullOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Null Orders.
    """

    delivery_postcode = DeliveryPostcodeSerializer(required=False)
    billing_postcode = BillingPostcodeSerializer(required=False)
    null_order_count = serializers.ReadOnlyField()

    class Meta:
        model = NullOrder
        fields = ['id', 'order_number', 'order_date', 'customer_age', 'order_quantity', 'toothbrush_type',
                  'delivery_postcode', 'billing_postcode', 'is_first', 'dispatch_status',
                  'dispatch_date', 'delivery_status', 'delivery_date', 'null_order_count']
        read_only_fields = ['null_order_count']
        list_serializer_class = BulkCreateOrderSerializer

    def create(self, validated_data):

        delivery_postcode = validated_data.pop('delivery_postcode', {})
        billing_postcode = validated_data.pop('billing_postcode', {})

        instance = NullOrder(**validated_data)
        # self._get_or_create_delivery_postcode(delivery_postcode, instance)
        # self._get_or_create_billing_postcode(billing_postcode, instance)

        if isinstance(self._kwargs['data'], dict):
            instance.save()

        return instance
    
    def _get_or_create_billing_postcode(self, postcode, order):

        billing_postcode = BillingPostcode.objects.create(
            **postcode
        )

        order.billing_postcode = billing_postcode
    
    def _get_or_create_delivery_postcode(self, postcode, order):

        delivery_postcode = DeliveryPostcode.objects.create(
            **postcode
        )

        order.delivery_postcode = delivery_postcode


class CountTBSerializer(serializers.ModelSerializer):
    """
    Serializer to display two fields only,
    pertaining to the amount of each toothbrush sold.
    """

    max_toothbrush_2000 = serializers.SerializerMethodField()
    max_toothbrush_4000 = serializers.SerializerMethodField()

    class Meta:
        model = FullOrder
        fields = ('max_toothbrush_2000','max_toothbrush_4000',)


    def get_max_toothbrush_2000(self, obj):
        return FullOrder.objects.filter(toothbrush_type='Toothbrush 2000').count()
    
    def get_max_toothbrush_4000(self, obj):
        return FullOrder.objects.filter(toothbrush_type='Toothbrush 4000').count()


class PostcodeFrequencySerializer(serializers.Serializer):

    delivery_postcode__postcode_area = serializers.CharField()
    postcode_count = serializers.IntegerField()


class AvgCustomerAgeSerializer(serializers.Serializer):

    avg_customer_age = serializers.IntegerField()


class DeliveryDeltaSerializer(serializers.Serializer):

    avg_delivery_delta = serializers.CharField()
    max_delivery_delta = serializers.CharField()
    min_delivery_delta = serializers.CharField()


class CustomerAgeSerializer(serializers.Serializer):

    avg_customer_age = serializers.IntegerField()
    max_customer_age = serializers.IntegerField()
    min_customer_age = serializers.IntegerField()


class FullPostcodeDataSerializer(serializers.Serializer):

    delivery_postcode__postcode_area = serializers.CharField()
    avg_customer_age = serializers.IntegerField()
    avg_delivery_delta = serializers.CharField()
    total_tb_sales = serializers.IntegerField()
    tb_2000_sales = serializers.IntegerField()
    tb_4000_sales = serializers.IntegerField()


class TB2000FullDataSerializer(serializers.Serializer):

    avg_customer_age = serializers.IntegerField()
    avg_delivery_delta = serializers.CharField()
    total_sales = serializers.IntegerField()

class TB4000FullDataSerializer(serializers.Serializer):

    avg_customer_age = serializers.IntegerField()
    avg_delivery_delta = serializers.CharField()
    total_sales = serializers.IntegerField()


class TBSalesByAgeSerializer(serializers.Serializer):

    customer_age = serializers.IntegerField()
    total_sales = serializers.IntegerField()


class OrderQuantitySerializer(serializers.Serializer):

    customer_age = serializers.IntegerField(required=False)
    delivery_postcode__postcode_area = serializers.CharField(required=False)
    order_quantity = serializers.IntegerField()