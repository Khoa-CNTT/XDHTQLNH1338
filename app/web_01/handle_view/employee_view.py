from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from django.db.models import Q, Sum, Count, F
from web_01.models import Employee, WorkShift

class EmployeeManagementView(LoginRequiredMixin, TemplateView):
    template_name = '/apps/web_01/employee/employee_list.html'

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

            # ✅ Mapping DataTables columns
            column_mapping = {
                0: "user_id",  
                1: "user__username",
                2: "salary",
                3: "total_shifts",
                4: "total_hours",
                5: "calculated_salary",
                6: "status",
                7: "shift_type",
                8: "created_at"
            }

            order_column = column_mapping.get(order_column_index, "user_id")
            if order_dir == "desc":
                order_column = "-" + order_column

            # ✅ Query danh sách nhân viên + Thống kê ca làm việc + Trạng thái & Loại ca
            employee_list = Employee.objects.select_related('user').filter(is_deleted=False) \
                .annotate(
                    total_shifts=Count('workshifts', filter=Q(workshifts__status="worked"), distinct=True),  
                    total_hours=Sum('workshifts__duration', filter=Q(workshifts__status="worked"), default=0),
                    calculated_salary=Sum(F('workshifts__duration') * F('salary') / 176, filter=Q(workshifts__status="worked"), default=0),
                    latest_shift_type=F('workshifts__shift_type'),  # Lấy loại ca mới nhất
                    latest_status=F('workshifts__status')  # Lấy trạng thái mới nhất
                )

            # ✅ Lọc theo từ khóa tìm kiếm
            if search_value:
                employee_list = employee_list.filter(
                    Q(user__username__icontains=search_value) |
                    Q(user__first_name__icontains=search_value) |
                    Q(user__last_name__icontains=search_value)
                )

            total_count = employee_list.count()
            employee_list = employee_list.order_by(order_column)[start:start + length]

            # ✅ Chuẩn bị dữ liệu JSON
            employees_data = []
            for index, employee in enumerate(employee_list, start=start):
                user = employee.user
                employees_data.append({
                    "index": index + 1,
                    "id": employee.user_id,  
                    "username": user.username if user else "N/A",
                    "salary": f"{employee.salary:,} VND",
                    "total_shifts": employee.total_shifts,
                    "total_hours": f"{employee.total_hours:.2f} giờ" if employee.total_hours else "0 giờ",
                    "calculated_salary": f"{employee.calculated_salary:,.0f} VND",
                    "status": employee.latest_status,  # ✅ Trả về trạng thái mới nhất
                    "shift_type": employee.latest_shift_type,  # ✅ Trả về loại ca mới nhất
                    "created_at": employee.formatted_created_at if employee.created_at else "",
                })

            return JsonResponse({
                "draw": draw,
                "recordsTotal": total_count,
                "recordsFiltered": total_count,
                "data": employees_data
            })

        except Exception as e:
            print("🔥 Exception:", str(e))
            return JsonResponse({"error": str(e)}, status=400)
