from django.urls import path

from .views import products_views, users, order_views

from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('api/products/', products_views.ProductListCreateAPIView.as_view()),
    path('api/products/info/', products_views.ProductInfoAPIView.as_view()),
    path('api/products/<int:product_id>/', products_views.ProductDetailAPIView.as_view()),

    path('users/', users.UserListView.as_view()),

    #     with templates
    path('products/', products_views.ProductListViewHTML.as_view(), name='product_list'),
    path('products/<int:product_id>/', products_views.ProductDetailViewHTML.as_view(), name='product_detail'),
    path('products/info/', products_views.ProductInfoAPIView.as_view()),
]

router = DefaultRouter()
router.register('orders', order_views.OrderViewSets)

urlpatterns += router.urls
