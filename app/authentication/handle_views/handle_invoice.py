from core.__Include_Library import *
from rest_framework.response import Response
from rest_framework import status
from authentication.mixins import AuthenticationPermissionMixin
from authentication.serializers import InvoiceSerializer
from web_01.models import Invoice, Cart, CartItem, Order, OrderDetail


class InvoiceViewSet(AuthenticationPermissionMixin, ViewSet):
    parser_classes = (JSONParser, MultiPartParser)
    # 🔄 Tạo Invoice từ Cart

    def create(self, request):
        customer = request.user.customer
        cart = get_object_or_404(Cart, customer=customer)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({'error': 'Giỏ hàng trống!'}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra session active
        active_session = customer.session_set.filter(status='active').first()
        if not active_session:
            return Response({'error': 'Không có session nào đang active!'}, status=status.HTTP_400_BAD_REQUEST)

        # Tạo Invoice
        invoice = Invoice.objects.create(
            session=active_session,
            total_amount=0  # Cập nhật sau
        )

        # Tạo Order
        order = Order.objects.create(invoice=invoice, total=0)  # Cập nhật sau
        total_amount = 0  # Khởi tạo tổng giá trị đơn hàng

        for item in cart_items:
            total_price = item.product.price * item.quantity
            OrderDetail.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                total=total_price
            )
            total_amount += total_price  # Cộng dồn vào tổng đơn hàng

        # Cập nhật tổng tiền vào Invoice & Order
        invoice.total_amount += total_amount
        order.total = total_amount
        invoice.save()
        order.save()

        # Xóa giỏ hàng
        cart_items.delete()

        # Trả về thông tin Invoice
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
