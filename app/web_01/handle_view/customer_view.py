from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from django.db.models import Q
from web_01.models import Customer


class CustomerManagementView(LoginRequiredMixin, TemplateView):
    template_name = '/apps/web_01/customer/customer_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            draw = int(request.POST.get("draw", 1))
            start = int(request.POST.get("start", 0))
            length = int(request.POST.get("length", 10))
            search_value = request.POST.get("search[value]", "").strip()

            order_column_index = int(request.POST.get("order[0][column]", 0))
            order_dir = request.POST.get("order[0][dir]", "asc")

            # ✅ Mapping column cho DataTables
            column_mapping = {
                0: "id",
                1: "user__username",
                # 2: "user__first_name",
                3: "loyalty_points",
                4: "created_at"
            }
            print("column_mapping", column_mapping)

            if order_column_index not in column_mapping:
                order_column_index = 0

            order_column = column_mapping[order_column_index]
            if order_dir == "desc":
                order_column = "-" + order_column

            # ✅ Query Customers
            customer_list = Customer.objects.select_related('user').filter(is_deleted=False)
            print('-----1------', customer_list)
            if search_value:
                customer_list = customer_list.filter(
                    Q(user__username__icontains=search_value) 
                    # Q(user__first_name__icontains=search_value) |
                    # Q(user__last_name__icontains=search_value)
                )

            total_count = customer_list.count()
            customer_list = customer_list.order_by(order_column)[start:start + length]

            # ✅ Chuẩn bị dữ liệu JSON trả về
            customers_data = [
                {
                    "index": index + 1,
                    "id": customer.id,
                    "username": customer.user.username if customer.user else "N/A",
                    # "first_name": customer.user.first_name if customer.user else "",
                    "loyalty_points": customer.loyalty_points,
                    "created_at": customer.formatted_created_at,
                }
                for index, customer in enumerate(customer_list, start=start)
            ]
            return JsonResponse({
                "draw": draw,
                "recordsTotal": total_count,
                "recordsFiltered": total_count,
                "data": customers_data
            }, safe=False)
            
            

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)