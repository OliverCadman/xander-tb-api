"""Serializers for the Orders API View."""

from rest_framework.serializers import ModelSerializer, ListSerializer
from core.models import FullOrder, TodaysOrder, NullOrder

from django.db import IntegrityError
from django.core.exceptions import ValidationError


class BulkCreateOrderSerializer(ListSerializer):
    def create(self, validated_data):
        res = [self.child.create(attrs) for attrs in validated_data]

        try:
            self.child.Meta.model.objects.bulk_create(res)
        except IntegrityError as e:
            raise ValidationError(e)

        return res


class FullOrderSerializer(ModelSerializer):

    class Meta:
        model = FullOrder
        exclude = ('id',)
        list_serializer_class = BulkCreateOrderSerializer

    def create(self, validated_data):
        instance = FullOrder(**validated_data)

        if isinstance(self._kwargs['data'], dict):
            instance.save()

        return instance


class TodaysOrderSerializer(ModelSerializer):

    class Meta:
        model = TodaysOrder
        exclude = ('id',)
        list_serializer_class = BulkCreateOrderSerializer

    def create(self, validated_data):
        instance = TodaysOrder(**validated_data)

        if isinstance(self._kwargs['data'], dict):
            instance.save()

        return instance


class NullOrderSerializer(ModelSerializer):

    class Meta:
        model = NullOrder
        exclude = ('id',)
        list_serializer_class = BulkCreateOrderSerializer

    def create(self, validated_data):
        instance = NullOrder(**validated_data)

        if isinstance(self._kwargs['data'], dict):
            instance.save()

        return instance
