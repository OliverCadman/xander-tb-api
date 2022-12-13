"""Serializers for the Orders API View."""

from rest_framework.serializers import ModelSerializer, ListSerializer
from core.models import FullOrder

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


class OrderSerializer(ModelSerializer):

    class Meta:
        model = FullOrder
        exclude = ('id',)
        list_serializer_class = BulkCreateOrderSerializer

    def create(self, validated_data):
        instance = FullOrder(**validated_data)

        if isinstance(self._kwargs['data'], dict):
            instance.save()

        return instance