"""Views for Orders API"""

from rest_framework import viewsets
from orders.serializers import (FullOrderSerializer,
                                TodaysOrderSerializer,
                                NullOrderSerializer,
                                CountTBSerializer)
from core.models import FullOrder, TodaysOrder, NullOrder
from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import action

from django.db.models import Count, Max


class FullOrderViewSet(viewsets.ModelViewSet):
    serializer_class = FullOrderSerializer
    queryset = FullOrder.objects.all()

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(FullOrderViewSet, self).get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_201_CREATED)


class TodaysOrderViewSet(viewsets.ModelViewSet):
    serializer_class = TodaysOrderSerializer
    queryset = TodaysOrder.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status.HTTP_201_CREATED
        )

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(TodaysOrderViewSet, self).get_serializer(
            *args, **kwargs)
    
    def get_queryset(self):
        """
        Return Todays Order objects with null values,
        if 'filter_by_null' specified in query params.
        """

        queryset = self.queryset

        if 'filter_by_null' in self.request.GET:
            return queryset.filter(
                delivery_status=None
            )
        return queryset
    


class NullOrderViewSet(viewsets.ModelViewSet):
    serializer_class = NullOrderSerializer
    queryset = NullOrder.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status.HTTP_201_CREATED
        )

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(NullOrderViewSet, self).get_serializer(*args, **kwargs)
    
    @action(methods=['DELETE'], detail=False)
    def delete(self, request):
        queryset = self.queryset
        queryset.delete()

        return Response(
            status.HTTP_204_NO_CONTENT
        )


class CountToothbrushTypesViewSet(viewsets.ModelViewSet):
    serializer_class = CountTBSerializer
    queryset = FullOrder.objects.filter(id=1)
    
