from django.db.models.aggregates import Max
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filter import InStockFilterBackend, OrderFilter, ProductFilter
from api.models import Order, Product, User
from api.serializers import (OrderCreateSerializer, OrderSerializer,
                             ProductInfoSerializer, ProductSerializer,
                             UserSerializer)


class ProductListCreateAPIView(generics.ListCreateAPIView):
    # filter.(stock__gt=0)
    queryset = Product.objects.order_by('pk')
    serializer_class = ProductSerializer

    filterset_class = ProductFilter

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend
    ]

    # =name search an exact match of the word
    search_fields = ["=name", "description"]
    ordering_fields = ["name", "price", "stock"]
    pagination_class = None

    # cache decorator for api endpoint
    @method_decorator(cache_page(60 * 15, key_prefix='product_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    #
    def get_queryset(self):
        import time
        time.sleep(2)
        return super().get_queryset()

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


# using model viewset inherits from generic view and includes implementation of different actions(CRUD OPERATIONS)
class OrderViewSets(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return OrderCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

    def user_orders(self, request):
        orders = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)

        return Response(serializer.data)


class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price'],
        })

        return Response(serializer.data)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None

#
#
#
#
#
# class OrderListAPIView(generics.ListAPIView):
#     # gt=0 gets all products with stock greater than 0
#     queryset = Order.objects.prefetch_related('items__product')
#     serializer_class = OrderSerializer
#
#
# class UserOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related('items__product')
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         qs = super().get_queryset()
#         return qs.filter(user=self.request.user)
#


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
