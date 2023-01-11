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
    TBSalesByAgeSerializer,
    OrderQuantitySerializer,
    TotalOrdersSerializer,
    DeliveryStatusSerializer
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
    def get_full_data(self, request):


        toothbrush_type = None
        data_by_postcode = None
        tb_sales_by_age = None
        total_orders = None
        delivery_statuses = None
        avg_delivery_delta = None

        if 'toothbrush_type' in request.query_params:
            toothbrush_type = ' '.join(request.query_params['toothbrush_type'].split('_'))

            total_orders = FullOrder.objects.filter(
                toothbrush_type__iexact=toothbrush_type).aggregate(
                total_orders=Count('order_quantity')
            )

            delivery_statuses = FullOrder.objects.filter(
                toothbrush_type__iexact=toothbrush_type).aggregate(
                delivery_successful=Count('pk', filter=Q(delivery_status='Delivered')),
                delivery_unsuccessful=Count('pk', filter=Q(delivery_status='Unsuccessful')),
                delivery_in_transit=Count('pk', filter=Q(delivery_status='In Transit'))
            )

            data_by_postcode = FullOrder.objects.filter(toothbrush_type__iexact=toothbrush_type).values(
            'delivery_postcode__postcode_area'
            ).annotate(
                avg_customer_age=Avg('customer_age'),
                total_tb_sales=Count('toothbrush_type'),
                avg_delivery_delta=Avg(F('delivery_date') - F('order_date')),
                tb_2000_sales=Count('pk', filter=Q(
                    toothbrush_type='Toothbrush 2000')),
                tb_4000_sales=Count('pk', filter=Q(
                    toothbrush_type='Toothbrush 4000')
                )
            ).order_by('-total_tb_sales')

            tb_sales_by_age = FullOrder.objects.filter(toothbrush_type__iexact=toothbrush_type).values(
                'customer_age'
            ).annotate(
                total_sales=Count('toothbrush_type')
            ).order_by('customer_age')

             # Delivery Deltas
            avg_delivery_delta = FullOrder.objects.filter(toothbrush_type__iexact=toothbrush_type).aggregate(
                avg_delivery_delta=Avg(F('delivery_date') - F('order_date')),
                max_delivery_delta=Max(F('delivery_date') - F('order_date')),
                min_delivery_delta=Min(F('delivery_date') - F('order_date'))
            )

            # Customer Ages
            customer_age = FullOrder.objects.filter(toothbrush_type__iexact=toothbrush_type).aggregate(
                avg_customer_age=Avg('customer_age'),
                max_customer_age=Max('customer_age'),
                min_customer_age=Min('customer_age')
            )
        
            data_by_postcode_serializer = FullPostcodeDataSerializer(data_by_postcode, many=True)
            tb_sales_by_age_serializer = TBSalesByAgeSerializer(tb_sales_by_age, many=True)
            total_orders_serializer = TotalOrdersSerializer(total_orders, many=False)
            delivery_status_serializer = DeliveryStatusSerializer(delivery_statuses, many=False)
            delivery_delta_serializer = DeliveryDeltaSerializer(avg_delivery_delta, many=False)
            customer_age_serializer = CustomerAgeSerializer(customer_age, many=False)

            return Response({
                'data_by_postcode': data_by_postcode_serializer.data,
                'sales_by_age': tb_sales_by_age_serializer.data,
                'total_orders': total_orders_serializer.data,
                'delivery_statuses': delivery_status_serializer.data,
                'avg_delivery_delta': delivery_delta_serializer.data,
                'customer_age': customer_age_serializer.data
            })

        total_orders = FullOrder.objects.aggregate(
            total_orders=Count('order_quantity')
        )

        delivery_statuses = FullOrder.objects.aggregate(
            delivery_successful=Count('pk', filter=Q(delivery_status='Delivered')),
            delivery_unsuccessful=Count('pk', filter=Q(delivery_status='Unsuccessful')),
            delivery_in_transit=Count('pk', filter=Q(delivery_status='In Transit'))
        )

        # Sales by Age
        tb_sales_by_age = FullOrder.objects.values(
                'customer_age'
            ).annotate(
                total_sales=Count('toothbrush_type')
            ).order_by('customer_age')
        
        # FullOrder data by postcode
        data_by_postcode = FullOrder.objects.values(
            'delivery_postcode__postcode_area'
        ).annotate(
            avg_customer_age=Avg('customer_age'),
            total_tb_sales=Count('toothbrush_type'),
            avg_delivery_delta=Avg(F('delivery_date') - F('order_date')),
            tb_2000_sales=Count('pk', filter=Q(
                toothbrush_type='Toothbrush 2000')),
            tb_4000_sales=Count('pk', filter=Q(
                toothbrush_type='Toothbrush 4000'))

        ).order_by('-total_tb_sales')

        # Customer Ages
        customer_age = FullOrder.objects.aggregate(
                avg_customer_age=Avg('customer_age'),
                max_customer_age=Max('customer_age'),
                min_customer_age=Min('customer_age')
            )
        
        # Delivery Deltas
        avg_delivery_delta = FullOrder.objects.aggregate(
            avg_delivery_delta=Avg(F('delivery_date') - F('order_date')),
            max_delivery_delta=Max(F('delivery_date') - F('order_date')),
            min_delivery_delta=Min(F('delivery_date') - F('order_date'))
        )

        # Toothbrush Sales per Age
        tb_sales_by_age = FullOrder.objects.values(
            'customer_age'
        ).annotate(
            total_sales=Count('toothbrush_type')
        ).order_by('customer_age')

        # Order Quantities 
        tb_2000_order_quantity = FullOrder.objects.filter(
                toothbrush_type='Toothbrush 2000'
            ).values('customer_age').annotate(
                order_quantity=Count('order_quantity')
            ).order_by('-order_quantity')
        

        tb_4000_order_quantity = FullOrder.objects.filter(
            toothbrush_type__iexact='Toothbrush 4000'
        ).values('customer_age').annotate(
            order_quantity=Count('order_quantity')
            ).order_by('-order_quantity')
        
        tb_2000_order_quantity_by_postcode = FullOrder.objects.filter(
            toothbrush_type='Toothbrush 2000'
        ).values('delivery_postcode__postcode_area').annotate(
            order_quantity=Count('order_quantity')
        ).order_by('-order_quantity')

        tb_4000_order_quantity_by_postcode = FullOrder.objects.filter(
            toothbrush_type='Toothbrush 4000'
        ).values('delivery_postcode__postcode_area').annotate(
            order_quantity=Count('order_quantity')
        ).order_by('-order_quantity')

        sales_by_age_serializer = TBSalesByAgeSerializer(tb_sales_by_age, many=True)
        data_by_postcode_serializer = FullPostcodeDataSerializer(data_by_postcode, many=True)
        customer_age_serializer = CustomerAgeSerializer(customer_age)
        avg_delivery_delta_serializer = DeliveryDeltaSerializer(avg_delivery_delta)
        tb_sales_by_age_serializer = TBSalesByAgeSerializer(tb_sales_by_age, many=True)
        tb_2000_order_quantity_serializer = OrderQuantitySerializer(tb_2000_order_quantity, many=True)
        tb_4000_order_quantity_serializer = OrderQuantitySerializer(tb_4000_order_quantity, many=True)
        tb_2000_order_quantity_by_postcode_serializer = OrderQuantitySerializer(tb_2000_order_quantity_by_postcode, many=True)
        tb_4000_order_quantity_by_postcode_serializer = OrderQuantitySerializer(tb_4000_order_quantity_by_postcode, many=True)
        total_orders_serializer = TotalOrdersSerializer(total_orders, many=False)
        delivery_status_serializer = DeliveryStatusSerializer(delivery_statuses, many=False)

        return Response({
            'total_orders': total_orders_serializer.data,
            'sales_by_age': sales_by_age_serializer.data,
            'data_by_postcode': data_by_postcode_serializer.data,
            'avg_delivery_delta': avg_delivery_delta_serializer.data,
            'customer_age': customer_age_serializer.data,
            'tb_sales_by_age': tb_sales_by_age_serializer.data,
            'tb_2000_orders_by_age': tb_2000_order_quantity_serializer.data,
            'tb_2000_orders_by_postcode': tb_2000_order_quantity_by_postcode_serializer.data,
            'tb_4000_orders_by_age': tb_4000_order_quantity_serializer.data,
            'tb_4000_orders_by_postcode': tb_4000_order_quantity_by_postcode_serializer.data,
            'delivery_statuses': delivery_status_serializer.data
        })
 

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'count_orders',
                OpenApiTypes.INT, enum=[0, 1],
                description='Find '
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
        queryset = self.queryset

        if 'filter_by_null' in self.request.GET:
            return queryset.filter(
                delivery_status=None
            )
        elif 'count_orders' in self.request.GET:
            return TodaysOrder.objects.aggregate(
                total_orders=Count('pk')
            )
            
        return queryset
    
    @action(methods=['GET'], detail=False)
    def count(self, request):
        todays_order_count = None
        toothbrush_type = None

        if 'toothbrush_type' in request.query_params:
            print('YES')
            toothbrush_type = ' '.join(request.query_params['toothbrush_type'].split('_'))
            todays_order_count = TodaysOrder.objects.filter(toothbrush_type__iexact=toothbrush_type).count()
        else:
            todays_order_count = TodaysOrder.objects.all().count()
        
        return Response({
            'count': todays_order_count
        })
    
    @action(methods=['DELETE'], detail=False)
    def delete(self, request):
        queryset = self.queryset
        queryset.delete()
        return Response(status.HTTP_204_NO_CONTENT)

    

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

