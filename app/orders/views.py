"""Views for Orders API"""

from rest_framework.generics import CreateAPIView
from orders.serializers import OrderSerializer


class OrderCreateView(CreateAPIView):
    serializer_class = OrderSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(OrderCreateView, self).get_serializer(*args, **kwargs)
