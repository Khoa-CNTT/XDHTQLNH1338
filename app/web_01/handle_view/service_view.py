
from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from django.views.decorators.csrf import csrf_exempt
from web_01.models import Table, Order, Product, Invoice, Session
from django import forms
from django.contrib.auth.decorators import login_required


class ServiceManagementView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/web_01/service/service_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tables = Table.objects.all()
        context['table_list'] = tables
        products = Product.objects.select_related('category').all()
        product_list = [
            {
                "id": product.id,
                "name": product.name,
                "image": getattr(product.image, 'url', None),
                "category": product.category.name or "Không có danh mục",
                "price": f"{product.price:,}đ",
            }
            for product in products
        ]
        context['product_list'] = product_list
        return context


@login_required
def get_order_by_table(request):
    table_id = request.GET.get('table_id')

    # Kiểm tra nếu không có table_id
    if not table_id:
        return JsonResponse({"success": False, "message": "Vui lòng chọn bàn!"}, status=400)

    # Lấy session đang hoạt động của bàn
    session = Session.objects.filter(table_id=table_id, status='active').select_related("customer", 'customer__user').first()

    if not session:
        return JsonResponse({"success": False, "message": "Bàn này chưa có khách hoặc chưa được mở!"}, status=404)

    # Lấy danh sách hóa đơn (Invoices) của bàn này
    invoices = session.invoice_set.prefetch_related("order_set__orderdetail_set__product").all()

    if not invoices.exists():
        return JsonResponse({"success": False, "message": "Bàn này chưa có đơn nào!"}, status=404)

    # Gộp tất cả các OrderDetail vào một danh sách duy nhất
    order_details_list = []
    total_amount = 0  # Tổng tiền của tất cả hóa đơn

    for invoice in invoices:
        for order in invoice.order_set.all():
            for detail in order.orderdetail_set.all():
                order_details_list.append({
                    "product_name": detail.product.name,
                    "quantity": detail.quantity,
                    "price": detail.price,
                    "total": detail.total,
                    "status": detail.status
                })
                total_amount += detail.total  # Cộng dồn tổng tiền

    # Lấy thông tin khách hàng (nếu có)
    customer_name = session.customer.user.username if session.customer else "Khách vãng lai"

    # Trả về template với danh sách đã gộp
    return render(request, "apps/web_01/service/order_item.html", {
        "order_details": order_details_list,
        "total_amount": total_amount,
        "customer_name": customer_name,
        "table_id": table_id
    })


@csrf_exempt
def order_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print('data', data)
            table_id = data.get("table_id")
            total = data.get("total")
            discount = data.get("discount_percent")
            payment_method = data.get("payment_method", "cash")  # Mặc định là tiền mặt

            # 🔹 Tìm session của bàn (giả sử có model Session liên kết)
            session = Session.objects.filter(table_id=table_id, status='active').first()

            if not session:
                return JsonResponse({"message": "Không tìm thấy session cho bàn này!", "status": "error"}, status=400)

            invoice = Invoice.objects.get(session=session)

            session.status = 'closed'
            session.table.status = 'available'
            invoice.payment_method = payment_method
            invoice.total_amount = total
            invoice.discount = discount
            invoice.order_set.all().update(status='completed')
            invoice.save()
            session.save()
            session.table.save()
            session.customer.loyalty_points = math.ceil(total / 10000) + session.customer.loyalty_points
            session.customer.save()

            return JsonResponse({
                "message": "Thanh toán thành công!",
                "invoice_id": invoice.id,
                "status": "success"
            })
        except Exception as e:
            return JsonResponse({"message": str(e), "status": "error"}, status=400)

    return JsonResponse({"message": "Phương thức không hợp lệ!"}, status=405)
