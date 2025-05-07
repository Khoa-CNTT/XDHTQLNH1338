from core.__Include_Library import *
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, F
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

            order_column_index = int(request.POST.get("order[0][column]", 0))
            order_dir = request.POST.get("order[0][dir]", "asc")

            # ✅ Mapping DataTables columns
            column_mapping = {
                0: "user_id",  
                1: "user__username",
                2: "role",
                3: "salary",
                4: "total_shifts",
                5: "total_hours",
                6: "calculated_salary",
                7: "created_at"
            }
            print("column_mapping", column_mapping)
            order_column = column_mapping.get(order_column_index, "user_id")
            if order_dir == "desc":
                order_column = "-" + order_column

            # ✅ Query danh sách nhân viên + Thống kê ca làm việc + Trạng thái & Loại ca
            employee_list = Employee.objects.select_related('user').filter(
                is_deleted=False
            ).exclude(role='chef').annotate(
                total_shifts=Count('workshifts', filter=Q(workshifts__status="worked"), distinct=True),  
                total_hours=Sum('workshifts__duration', filter=Q(workshifts__status="worked"), default=0),
                calculated_salary=Sum(F('workshifts__duration') * F('salary') / 176, filter=Q(workshifts__status="worked"), default=0),
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
                    "role": employee.role,  # Đảm bảo field này tồn tại
                    "salary": f"{employee.salary:,} VND",
                    "total_shifts": employee.total_shifts,
                    "total_hours": f"{employee.total_hours:.2f} giờ",
                    "calculated_salary": f"{employee.calculated_salary:,.0f} VND",
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
        shift_type = request.POST.get('shift_type')
        status = request.POST.get('status')
        role = request.POST.get('role')  # Get role from form
        
        # Validate input
        if not all([employee_id, username, salary, shift_type, status]):
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
            shift_type=shift_type
        ).first()
        
        if existing_shift:
            # Update existing shift
            existing_shift.status = status
            existing_shift.save()
        else:
            # Create new shift
            WorkShift.objects.create(
                employee=employee,
                date=current_date,  # Add the date field
                shift_type=shift_type,
                status=status,
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

