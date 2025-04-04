
from core.__Include_Library import *
from web_01.models import Product, CartItem, Cart, OrderDetail, Order, Invoice, Table, TableReservation, Category
from django.conf import settings


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)  # Hiển thị tên Category
    image_url = serializers.SerializerMethodField()  # Trả về URL đầy đủ

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price', 'description', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return obj.image.url
        return None


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.IntegerField(source='product.price', read_only=True)
    product_image_url = serializers.SerializerMethodField()  # Trả về URL đầy đủ  # Trả về URL đầy đủ

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_image_url', 'product_price', 'quantity']

    def get_product_image_url(self, obj):
        request = self.context.get('request')
        if obj.product.image:
            return obj.product.image.url
        return None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'items']


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['product', 'quantity', 'price', 'total']


class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, source='orderdetail_set')

    class Meta:
        model = Order
        fields = ['id', 'total', 'status', 'order_details']


class InvoiceSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, source='order_set')

    class Meta:
        model = Invoice
        fields = ['id', 'session', 'total_amount', 'payment_method', 'orders', 'created_at']


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'status', 'qr_image']


class TableReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableReservation
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'status']
