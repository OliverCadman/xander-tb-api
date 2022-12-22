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

<<<<<<< HEAD
from django.db.models import Count, Max
=======
from django.db.models import Max

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)
>>>>>>> 26cbe247ff7daa771a63c2a52b005cb9ee58f067


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

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'find_max',
                OpenApiTypes.INT, enum=[0, 1],
                description='Find Max Order Number'
            ),
            OpenApiParameter(
                'find_null',
                OpenApiTypes.INT, enum=[0, 1],
                description='Find all null orders'
            )
        ]
    )
)
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

        find_max = bool(
            int(self.request.query_params.get('find_max', 0))
        )

        queryset = self.queryset

        if 'filter_by_null' in self.request.GET:
            return queryset.filter(
                delivery_status=None
            )
        elif find_max:
            max_number = queryset.aggregate(Max('order_number'))
            print('MAX NUMBER???', max_number)
            return queryset.filter(order_number=max_number['order_number__max'])
            
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
    
