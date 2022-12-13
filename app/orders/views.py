"""Views for Orders API"""

from rest_framework.generics import CreateAPIView
from orders.serializers import (FullOrderSerializer,
                                TodaysOrderSerializer,
                                NullOrderSerializer)


class FullOrderCreateView(CreateAPIView):
    serializer_class = FullOrderSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(FullOrderCreateView, self).get_serializer(*args, **kwargs)


class TodaysOrderCreateView(CreateAPIView):
    serializer_class = TodaysOrderSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(TodaysOrderCreateView, self).get_serializer(
            *args, **kwargs)


class NullOrderCreateView(CreateAPIView):
    serializer_class = NullOrderSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(NullOrderCreateView, self).get_serializer(*args, **kwargs)
