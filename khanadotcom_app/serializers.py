from rest_framework import serializers
from .models import (
    Order,
    OrderItem,
    CustomerDetail,
    RestaurantOwner,
    DeliveryPerson,
    Restaurant,
    MenuItem
)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "menu_item",
            "quantity",
            "price",
        )  # Adjust fields as per your OrderItem model


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source="orderitem_set", many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "order_id",
            "user",
            "delivery_address",
            "total_amount",
            "order_date",
            "items",
        )


class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetail
        fields = "__all__"


class RestaurantOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantOwner
        fields = "__all__"


class DeliveryPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPerson
        fields = "__all__"


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
        
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['menu_item_id', 'restaurant', 'name', 'description', 'price', 'menu_item_pic', 'availability', 'rating', 'preparation_time']