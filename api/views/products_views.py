from django.db.models.aggregates import Max
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from api.filter import InStockFilterBackend, ProductFilter
from api.models import Product
from api.serializers import (ProductInfoSerializer, ProductSerializer)


class ProductListCreateAPIView(generics.ListCreateAPIView):
    throttle_scope = 'products'
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


# html templates
class ProductListViewHTML(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    ordering = ['pk']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('pk')


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


class ProductDetailViewHTML(DetailView):
    model = Product
    pk_url_kwarg = 'product_id'
    template_name = 'products/product_detail.html'
    context_object_name = 'product'


class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price'],
        })

        return Response(serializer.data)
