from django.db.models.aggregates import Max
from api.filter import ProductFilter, InStockFilterBackend
from api.serializers import ProductSerializer, OrderSerializer, OrderItemSerializer, ProductInfoSerializer
from rest_framework.response import Response

from api.models import Product, Order, OrderItem
from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny
)
from rest_framework.views import APIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
class ProductListCreateAPIView(generics.ListCreateAPIView):
    # filter.(stock__gt=0)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filterset_class = ProductFilter

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend
    ]

    # =name search an exact match of the word
    search_fields = ["name","description"]
    ordering_fields = ["name","price","stock"]

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


# automatically get the primary key out of the url
class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_id'

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class OrderListAPIView(generics.ListAPIView):
    # gt=0 gets all products with stock greater than 0
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer


class UserOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price'],
        })

        return Response(serializer.data)










# @api_view(['GET'])
# def product_list(request):
#     products = Product.objects.all()
#     serializer = ProductSerializer(products, many=True)
#
#     return Response(serializer.data)



# @api_view(['GET'])
# def product_detail(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     serializer = ProductSerializer(product)
#
#     return Response(serializer.data)
# @api_view(['GET'])
# def order_list(request):
#     # optimize the backend by prefetching the orders, following form item to prodcut using foreign key
#     orders = Order.objects.prefetch_related('items__product').all()
#     serializer = OrderSerializer(orders, many=True)
#
#     return Response(serializer.data)
