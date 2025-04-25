from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from django.db.models import Q
from web_01.models import Order, OrderDetail


class OrderManagementView(LoginRequiredMixin, TemplateView):
    template_name = '/apps/web_01/order/order_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, **kwargs):
        try:
            # Lấy params từ request
            params = json.loads(request.POST.get('params', '{}'))

            search_value = params.get('search', '').strip()
            start = int(params.get('start', 0))
            length = int(params.get('length', 10))
            order_column_index = int(params.get('order_column', 0))
            order_dir = params.get('order_dir', 'asc')

            # Mapping cột DataTables với DB
            column_mapping = {
                0: "id",
                1: "invoice__session__customer__name",
                2: "invoice__session__table__name",
                3: "total",
                4: "created_at"
            }
            order_column = column_mapping.get(order_column_index, "id")
            if order_dir == "desc":
                order_column = "-" + order_column

            # Query dữ liệu từ DB
            order_list = Order.objects.select_related(
                'invoice__session__customer',
                'invoice__session__table'
            )

            if search_value:
                order_list = order_list.filter(
                    Q(invoice__session__customer__name__icontains=search_value) |
                    Q(invoice__session__table__name__icontains=search_value)
                )

            total_count = order_list.count()
            order_list = order_list.order_by(order_column)[start:start + length]

            # Chuyển dữ liệu sang JSON
            orders_data = [
                {
                    "index": index + 1,
                    "id": order.id,
                    "username": (
                        f"{order.invoice.session.customer.user.username}"
                    ),
                    "first_name": (
                        f"{order.invoice.session.customer.user.first_name}"
                    ),
                    "table": (
                        f'Bàn {order.invoice.session.table.table_number}'
                        if order.invoice.session.table else "Không có bàn"
                    ),
                    "total": order.formatted_price,
                    "formatted_created_at": order.formatted_created_at,
                    "status": order.status,
                    "status_display": order.get_status_display()
                }
                for index, order in enumerate(order_list, start=start)
            ]

            return JsonResponse({
                "draw": params.get('draw', 1),
                "recordsTotal": total_count,
                "recordsFiltered": total_count,
                "data": orders_data
            })

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            return JsonResponse({"error": str(e)}, status=400)


@login_required
def detail_order(request, id):
    order = get_object_or_404(
        Order.objects.select_related(
            "invoice", "invoice__session", "invoice__session__customer"
        ),
        id=id
    )

    # Lấy danh sách món ăn trong đơn, tối ưu bằng prefetch_related
    order_details = OrderDetail.objects.filter(order=order).exclude(status='cancelled').select_related("product")

    context = {
        "order": order,
        "order_details": order_details
    }
    return render(request, "apps/web_01/modal/content/content_detail_order.html", context)
