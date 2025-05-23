from core.__Include_Library import *
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, F, ExpressionWrapper, DurationField, Case, When, FloatField, Value
from web_01.models import Employee, WorkShift, User
from django.utils import timezone
import datetime
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

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

            filter_name = request.POST.get("filter_name", "").strip()
            filter_role = request.POST.get("filter_role", "").strip()

            order_column_index = int(request.POST.get("order[0][column]", 0))
            order_dir = request.POST.get("order[0][dir]", "desc")

            column_mapping = {
                0: "user_id",
                1: "user__username",
                2: "role",
                3: "salary",
                4: "total_shifts",
                5: "total_hours",
                6: "actual_salary",
                7: "created_at"
            }
            order_column = column_mapping.get(order_column_index, "user_id")
            if order_dir == "desc":
                order_column = "-" + order_column

            employees = Employee.objects.select_related('user') \
                .filter(~Q(role__iexact='chef'), is_deleted=False) \
                .annotate(
                    total_shifts=Sum(
                        Case(
                            When(
                                Q(workshifts__time_start__isnull=False) & Q(workshifts__time_end__isnull=False) &
                                Q(workshifts__shift_type='allday'),
                                then=Value(1.0)
                            ),
                            When(
                                Q(workshifts__time_start__isnull=False) & Q(workshifts__time_end__isnull=False),
                                then=Value(0.5)
                            ),
                            default=Value(0.0),
                            output_field=FloatField()
                        )
                    ),
                    total_hours=Sum(
                        Case(
                            When(
                                Q(workshifts__time_start__isnull=False) & Q(workshifts__time_end__isnull=False) &
                                Q(workshifts__shift_type='allday'),
                                then=Value(8.0)
                            ),
                            When(
                                Q(workshifts__time_start__isnull=False) & Q(workshifts__time_end__isnull=False),
                                then=Value(4.0)
                            ),
                            default=Value(0.0),
                            output_field=FloatField()
                        )
                    )
                )

            if filter_name:
                employees = employees.filter(
                    Q(user__username__icontains=filter_name) |
                    Q(user__first_name__icontains=filter_name) |
                    Q(user__last_name__icontains=filter_name)
                )

            if filter_role:
                employees = employees.filter(role=filter_role)

            if search_value:
                employees = employees.filter(
                    Q(user__username__icontains=search_value) |
                    Q(user__first_name__icontains=search_value) |
                    Q(user__last_name__icontains=search_value)
                )

            total_count = employees.count()
            employees = employees.order_by(order_column)[start:start + length]

            employees_data = []
            for index, employee in enumerate(employees, start=start + 1):
                total_shifts = employee.total_shifts or 0.0
                total_hours = employee.total_hours or 0.0

                hourly_rate = employee.salary / 176  # giả định chuẩn 176 giờ/tháng
                actual_salary = total_hours * hourly_rate

                employees_data.append({
                    "index": index,
                    "id": employee.user_id,
                    "username": employee.user.username,
                    "role": employee.role,
                    "salary": f"{employee.salary:,} VND",
                    "total_shifts": f"{total_shifts:.1f}",
                    "total_hours": f"{total_hours:.2f} giờ",
                    "actual_salary": f"{actual_salary:,.0f} VND",
                    "created_at": employee.user.date_joined.strftime('%d/%m/%Y') if hasattr(employee.user, 'date_joined') else ""
                })

            return JsonResponse({
                "draw": draw,
                "recordsTotal": total_count,
                "recordsFiltered": total_count,
                "data": employees_data
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
@login_required
def employee_add(request):
    """Thêm nhân viên mới"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ'})
    
    try:
        username = request.POST.get('username')
        salary = request.POST.get('salary')
        role = request.POST.get('role', 'staff')  # Default to 'staff' if not provided
        total_shifts = request.POST.get('total_shifts', '0')
        total_hours = request.POST.get('total_hours', '0')
        
        # Validate input
        if not all([username, salary]):
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng điền đầy đủ thông tin'
            })
        
        # Convert salary to integer (remove commas)
        try:
            salary = int(salary.replace(',', ''))
            total_shifts = int(total_shifts)
            total_hours = float(total_hours.replace(' giờ', '').strip())
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Dữ liệu không hợp lệ'
            })
        
        # Check if user exists
        user = User.objects.filter(username=username).first()
        if not user:
            # Create new user if not exists
            user = User.objects.create(
                username=username,
                first_name=username,
                is_active=True
            )
        
        # Create employee
        employee = Employee.objects.create(
            user=user,
            salary=salary,
            role=role 
        )
        
        # Create initial work shift with current date
        if total_shifts > 0:
            current_date = timezone.now().date()
            hours_per_shift = total_hours / total_shifts if total_shifts > 0 else 0
            
            # Create shifts for the employee
            for i in range(total_shifts):
                shift_date = current_date - datetime.timedelta(days=i)
                WorkShift.objects.create(
                    employee=employee,
                    date=shift_date,
                    duration=hours_per_shift
                )
        
        return JsonResponse({
            'success': True,
            'message': 'Thêm nhân viên thành công'
        })
        
        
    except Exception as e:
        print("🔥 Exception:", str(e))
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

@login_required
def employee_update(request):
    """Cập nhật thông tin nhân viên"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ'})
    
    try:
        employee_id = request.POST.get('employee_id')
        username = request.POST.get('username')
        salary = request.POST.get('salary')
        role = request.POST.get('role')  # Get role from form
        
        # Validate input
        if not all([employee_id, username, salary]):
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng điền đầy đủ thông tin'
            })
        
        # Convert salary to integer (remove commas)
        try:
            salary = int(salary.replace(',', ''))
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Lương không hợp lệ'
            })
        
        # Get employee
        employee = Employee.objects.filter(user_id=employee_id, is_deleted=False).first()
        if not employee:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy nhân viên'
            })
        
        # Update employee
        employee.salary = salary
        if role:
            employee.role = role  # Update role if provided
        employee.save()
        
        # Update user
        user = employee.user
        if user:
            user.username = username
            user.save()
        
        # Create new work shift with updated status and type
        current_date = timezone.now().date()
        
        # Check if a shift already exists for this employee, date, and shift type
        existing_shift = WorkShift.objects.filter(
            employee=employee,
            date=current_date,
        ).first()
        
        if existing_shift:
            # Update existing shift
            existing_shift.save()
        else:
            # Create new shift
            WorkShift.objects.create(
                employee=employee,
                date=current_date,  # Add the date field
                duration=4.0  # Default duration is 4 hours
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Cập nhật nhân viên thành công'
        })
        
    except Exception as e:
        print("🔥 Exception:", str(e))
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

@login_required
def employee_delete(request):
    """Xóa nhân viên (soft delete)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ'})
    
    try:
        employee_id = request.POST.get('employee_id')
        
        # Validate input
        if not employee_id:
            return JsonResponse({
                'success': False,
                'message': 'ID nhân viên không hợp lệ'
            })
        
        # Get employee
        employee = Employee.objects.filter(user_id=employee_id, is_deleted=False).first()
        if not employee:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy nhân viên'
            })
        
        # Soft delete employee
        employee.is_deleted = True
        employee.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Xóa nhân viên thành công'
        })
        
    except Exception as e:
        print("🔥 Exception:", str(e))
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

