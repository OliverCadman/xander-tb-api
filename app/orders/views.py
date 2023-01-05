"""Views for Orders API"""

from rest_framework import viewsets
from orders.serializers import (
    FullOrderSerializer,
    TodaysOrderSerializer,
    NullOrderSerializer,
    CountTBSerializer,
    DeliveryPostcodeSerializer,
    BillingPostcodeSerializer,
    PostcodeFrequencySerializer,
    AvgCustomerAgeSerializer,
    DeliveryDeltaSerializer,
    FullPostcodeDataSerializer,
    CustomerAgeSerializer,
    TB2000FullDataSerializer,
    TBSalesByAgeSerializer
)
from core.models import (
    FullOrder,
    TodaysOrder,
    NullOrder,
    DeliveryPostcode,
    BillingPostcode
)

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from django.db.models import Count, Avg, Max, Min, F, When, Case, Q

from functools import reduce
import operator

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)

import csv

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'postal_region',
                 OpenApiTypes.STR,
                description='Search by postcode area'
            ),
        ]
    )
)
class FullOrderViewSet(viewsets.ModelViewSet):
    serializer_class = FullOrderSerializer
    queryset = FullOrder.objects.all()

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(FullOrderViewSet, self).get_serializer(*args, **kwargs)
    
    def get_serializer_class(self):
        """Return specific serializer for request."""
    
        if self.action == 'get_total_sales_by_postcode':
            return PostcodeFrequencySerializer
        elif self.action == 'get_avg_customer_age':
            return AvgCustomerAgeSerializer
        elif self.action == 'get_full_data_by_postcode':
            return FullPostcodeDataSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):


        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_201_CREATED)
    
    def get_queryset(self):
        queryset = self.queryset

        if 'postal_region' in self.request.query_params:
            region = self.request.query_params['postal_region']
            queryset = FullOrder.objects.filter(delivery_postcode__contains=region)
            return queryset
        elif 'avg_customer_age' in self.request.query_params:
            queryset = FullOrder.objects.aggregate(avg_customer_age=Avg('customer_age'))
            print(queryset)
        
        return queryset
    
    @action(detail=False)
    def get_total_sales_by_postcode(self, request):
        """
        Get total toothbrush sales by postcode area.

        Returns total sales of all toothbrush types per
        postcode area, or sales of individual toothbrush types
        if included in request query params.
        """
        toothbrush_type = None
        if 'toothbrush_type' in request.query_params:
            toothbrush_type = request.query_params['toothbrush_type']

        if toothbrush_type == 'toothbrush_2000':
            sales_by_postcode = FullOrder.objects.filter(toothbrush_type='Toothbrush 2000').values(
                'delivery_postcode__postcode_area'
            ).annotate(
                postcode_count=Count('delivery_postcode__postcode_area')).\
                    order_by('-postcode_count')
        elif toothbrush_type == 'toothbrush_4000':
            """Get sum of toothbrushes sold for each postcode area in DB."""
            sales_by_postcode = FullOrder.objects.filter(toothbrush_type='Toothbrush 4000').values(
                    'delivery_postcode__postcode_area'
                ).annotate(
                    postcode_count=Count('delivery_postcode__postcode_area')).\
                        order_by('-postcode_count')
        else:
            sales_by_postcode = FullOrder.objects.values(
                    'delivery_postcode__postcode_area'
                ).annotate(
                    postcode_count=Count('toothbrush_type')
                ).order_by('-postcode_count')

        serializer = self.get_serializer(sales_by_postcode, many=True)

        return Response(serializer.data)
    
    @action(detail=False)
    def get_full_data_by_tb_type(self, request):
        """
        Return comprehensive data for each
        toothbrush type.
        """

        data_by_toothbrush = None
        toothbrush_type = None

        toothbrush_type = ' '.join(request.query_params['toothbrush_type'].split('_'))

        if toothbrush_type == 'toothbrush 2000':
            data_by_toothbrush = FullOrder.objects.filter(
                toothbrush_type__iexact=toothbrush_type
            ).aggregate(
                avg_customer_age=Avg('customer_age'),
                avg_delivery_delta=Avg(F('delivery_date') - F('order_date')),
                total_sales=Count('toothbrush_type')
            )
        else:
            data_by_toothbrush = FullOrder.objects.filter(
                toothbrush_type__iexact=toothbrush_type
            ).aggregate(
                avg_customer_age=Avg('customer_age'),
                avg_delivery_delta=Avg(F('delivery_date') - F('order_date')),
                total_sales=Count('toothbrush_type')
            )
        
        serializer = TB2000FullDataSerializer(data_by_toothbrush)

        return Response(serializer.data)

    
    @action(detail=False)
    def get_full_data_by_postcode(self, request):
        """
        Return a comprehensive data for
        each postcode.
        """

        data_by_postcode = None
        toothbrush_type = None

        if 'toothbrush_type' in request.query_params:

            toothbrush_type = ' '.join(request.query_params['toothbrush_type'].split('_'))
                
            data_by_postcode = FullOrder.objects.filter(
                toothbrush_type__iexact=toothbrush_type
            ).values(
                'delivery_postcode__postcode_area'
            ).annotate(
                avg_customer_age=Avg('customer_age'),
                total_tb_sales=Count('toothbrush_type'),
                avg_delivery_delta=Avg(
                    F('delivery_date') - F('order_date')),
                tb_2000_sales=Count('pk', filter=Q(
                    toothbrush_type='Toothbrush 2000')),
                tb_4000_sales=Count('pk', filter=Q(
                    toothbrush_type='Toothbrush 4000'))

            ).order_by('-total_tb_sales')
        else:   
            data_by_postcode = FullOrder.objects.values(
                'delivery_postcode__postcode_area'
            ).annotate(
                avg_customer_age=Avg('customer_age'),
                total_tb_sales=Count('toothbrush_type'),
                avg_delivery_delta=Avg(F('delivery_date') - F('order_date')),
                tb_2000_sales=Count('pk', filter=Q(toothbrush_type='Toothbrush 2000')),
                tb_4000_sales=Count('pk', filter=Q(toothbrush_type='Toothbrush 4000'))
        
            ).order_by('-total_tb_sales')

        serializer = self.get_serializer(data_by_postcode, many=True)

        return Response(serializer.data)

    @action(detail=False)
    def get_delivery_deltas(self, request):

        toothbrush_type = None
        avg_delivery_delta = None

        if 'toothbrush_type' in request.query_params:
            toothbrush_type = ' '.join(
                request.query_params['toothbrush_type'].split('_'))
            
            avg_delivery_delta = FullOrder.objects.filter(
                toothbrush_type__iexact=toothbrush_type
            ).aggregate(
            avg_delivery_delta=Avg(F('delivery_date') - F('order_date')),
            max_delivery_delta=Max(F('delivery_date') - F('order_date')),
            min_delivery_delta=Min(F('delivery_date') - F('order_date'))
        )
        else:
            avg_delivery_delta = FullOrder.objects.aggregate(
                avg_delivery_delta=Avg(F('delivery_date') - F('order_date')),
                max_delivery_delta=Max(F('delivery_date') - F('order_date')),
                min_delivery_delta=Min(F('delivery_date') - F('order_date'))
            )

        serializer = DeliveryDeltaSerializer(avg_delivery_delta)

        return Response(serializer.data)
    
    @action(detail=False)
    def get_avg_customer_age(self, request):
        """
        Return the average age of customer for all toothbrushes,
        filterable by toothbrush type, and by postcode area.
        """

        toothbrush_type = None
        postcode_area = None

        if 'postcode_area' in request.query_params:
            postcode_area = request.query_params['postcode_area']

            average_customer_age = FullOrder.objects.filter(
                delivery_postcode__postcode_area__in=postcode_area
            ).aggregate(
                avg_customer_age=Avg('customer_age')
            )
        elif 'toothbrush_type' in request.query_params:
            toothbrush_type = ' '.join(request.query_params['toothbrush_type'].split('_'))
            average_customer_age = FullOrder.objects.filter(
                toothbrush_type__iexact=toothbrush_type
            ).aggregate(avg_customer_age=Avg('customer_age'))
        else:
            average_customer_age = FullOrder.objects.aggregate(
                avg_customer_age=Avg('customer_age')
            )

        serializer = AvgCustomerAgeSerializer(average_customer_age)

        return Response(serializer.data)
    
    @action(detail=False)
    def get_customer_ages(self, request):

        toothbrush_type = None
        customer_age = None

        if 'toothbrush_type' in request.query_params:
            toothbrush_type = ' '.join(
                request.query_params['toothbrush_type'].split('_'))

            customer_age = FullOrder.objects.filter(
                toothbrush_type__iexact=toothbrush_type
            ).aggregate(
            avg_customer_age=Avg('customer_age'),
            max_customer_age=Max('customer_age'),
            min_customer_age=Min('customer_age')
        )
        else:
            customer_age = FullOrder.objects.aggregate(
                avg_customer_age=Avg('customer_age'),
                max_customer_age=Max('customer_age'),
                min_customer_age=Min('customer_age')
            )

        serializer = CustomerAgeSerializer(customer_age)
        return Response(serializer.data)
    
    @action(detail=False)
    def get_tb_sales_by_age(self, request):

        toothbrush_type = None
        tb_sales_by_age = None

        if 'toothbrush_type' in request.query_params:
            toothbrush_type = ' '.join(request.query_params['toothbrush_type'].split('_'))

            tb_sales_by_age = tb_sales_by_age = FullOrder.objects.filter(
                toothbrush_type__iexact=toothbrush_type
            ).values(
            'customer_age'
        ).annotate(
            total_sales=Count('toothbrush_type')
        ).order_by('customer_age')
        else:
            tb_sales_by_age = FullOrder.objects.values(
                'customer_age'
            ).annotate(
                total_sales=Count('toothbrush_type')
            ).order_by('customer_age')

        serializer = TBSalesByAgeSerializer(tb_sales_by_age, many=True)
        return Response(serializer.data)



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
    
    def get_queryset(self):
        queryset = self.queryset

        toothbrush_type = None

        if 'count_null_orders' in self.request.query_params:
            print('HEYYYY')
            if 'toothbrush_type' in self.request.query_params:
                toothbrush_type = ' '.join(request.query_params['toothbrush_type'].split('_'))
                queryset = NullOrder.objects.filter(
                    toothbrush_type__iexact=toothbrush_type
                ).aggregate(null_order_count=Count('id'))

                return queryset
        else:
            queryset = NullOrder.objects.aggregate(null_order_count=Count('id'))

        return queryset
    

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
    
    @action(detail=False)
    def get_null_orders(self, request):
        """Retrieve and return null orders."""

        null_orders = None
        toothbrush_type = None

        if 'toothbrush_type' in request.query_params:
            toothbrush_type = ' '.join(request.query_params['toothbrush_type'].split('_'))
            null_orders = NullOrder.objects.filter(
                toothbrush_type__iexact=toothbrush_type
            ).aggregate(
                null_order_count=Count('id')
            )
        else:
            toothbrush_type = NullOrder.objects.aggregate(
                null_order_count=Count('id')
            )
        
        serializer = NullOrderCountSerializer(null_orders, many=True)
        return Response(serializer.data)


class CountToothbrushTypesViewSet(viewsets.ModelViewSet):
    serializer_class = CountTBSerializer
    queryset = FullOrder.objects.filter(id=1)
    

class DeliveryPostcodeViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryPostcodeSerializer
    queryset = DeliveryPostcode.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status.HTTP_201_CREATED
        )


class BillingPostcodeViewset(viewsets.ModelViewSet):
    serializer_class = BillingPostcodeSerializer
    queryset = BillingPostcode.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status.HTTP_201_CREATED
        )

