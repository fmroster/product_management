from django.db import transaction
from rest_framework import serializers

from .models import Order, OrderItem, Product, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # bad method because it can return sensitive data
        # fields = '__all__'
        fields = ('email', 'username', 'get_full_name', 'orders')



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'name',
            'description',
            'price',
            'stock',
        )

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Price cannot be negative')
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            'product_name',
            'product_price',
            'quantity',
            'item_subtotal'
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = (
                'product',
                'quantity'
            )

    items = OrderItemCreateSerializer(many=True, required=False)

    def update(self, instance, validated_data):
        orderitem_data = validated_data.pop('items')

        # remove the existing items, and rewrites them, if it fails it will revert
        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if orderitem_data is not None:
                # clear existing items (optional, depends on requirements)
                instance.items.all().delete()

                # recreate items with updated data
                for item in orderitem_data:
                    OrderItem.objects.create(order=instance, **item)

        return instance

    def create(self, validated_data):
        orderitem_data = validated_data.pop('items')

        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for item in orderitem_data:
                OrderItem.objects.create(order=order, **item)

        return order

    class Meta:
        model = Order
        fields = (
            'user',
            'status',
            'items'
        )
        # other way of passing read only fields
        extra_kwargs = {
            'user': {'read_only': True},
        }


class OrderSerializer(serializers.ModelSerializer):
    # order item fields in the order, will be serialised using the OrderItemSerializer, other fields will be realised normally
    # many items can be serialised all at once and cannot be writable withing the order serializer

    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='total')

    # get a list of order items loop through and get the sum
    def total(self, obj):
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items)

    class Meta:
        model = Order
        fields = ('order_id', 'created_at', 'user', 'status', 'items', 'total_price')


class ProductInfoSerializer(serializers.Serializer):
    # get all products, count and max price of product
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()
