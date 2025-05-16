from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from django.db.models import Q
from web_01.models import TableReservation, Table
from django.views.decorators.http import require_POST
from datetime import date as current_date


class TableReservationManagementView(LoginRequiredMixin, TemplateView):
    template_name = '/apps/web_01/table_reservation/table_reservation_list.html'

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
            order_dir = request.POST.get("order[0][dir]", "desc")
            name = request.POST.get("name", "").strip()
            phone_number = request.POST.get("phone_number", "").strip()
            table_number = request.POST.get("table_number", "").strip()
            

            column_mapping = {
                0: "name",
                1: "phone_number",
                2: "many_person",
                3: "table__table_number",
                4: "date",
                5: "hour",
                6: "status",
                7: "created_at"
            }

            order_column = column_mapping.get(order_column_index, "created_at")
            if order_dir == "desc":
                order_column = "-" + order_column

            reservations = TableReservation.objects.select_related("table")

            if search_value:
                reservations = reservations.filter(
                    Q(name__icontains=search_value) |
                    Q(phone_number__icontains=search_value) |
                    Q(table__table_number__icontains=search_value)
                )
            
            if name:
                reservations = reservations.filter(name__icontains=name)
            if phone_number:
                reservations = reservations.filter(phone_number__icontains=phone_number)
            if table_number:
                reservations = reservations.filter(table__table_number__icontains=table_number)

            total_count = reservations.count()
            reservations = reservations.order_by(order_column)[start:start + length]

            data = []
            for index, r in enumerate(reservations, start=start):
                data.append({
                    "id": r.id,
                    "index": index + 1,
                    "name": r.name,
                    "phone_number": r.phone_number,
                    "many_person": r.many_person,
                    "table_number": r.table.table_number if r.table else "N/A",
                    "date": r.date.strftime('%d/%m/%Y'),
                    "hour": r.hour.strftime('%H:%M'),
                    "status": r.get_status_display(),
                    "created_at": r.created_at.strftime('%d/%m/%Y %H:%M'),
                })

            return JsonResponse({
                "draw": draw,
                "recordsTotal": total_count,
                "recordsFiltered": total_count,
                "data": data
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
class TableReservationForm(forms.ModelForm):
    class Meta:
        model = TableReservation
        fields = ['table', 'date', 'status']  
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'table': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

        
@login_required
def edit_table_reservation(request, id):
    """Xử lý chỉnh sửa đặt bàn (bàn, ngày, trạng thái) bằng AJAX"""
    reservation = get_object_or_404(TableReservation, id=id)

    if request.method == "POST":
        form = TableReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            if form.cleaned_data.get('date') < current_date.today():
                return JsonResponse({
                    "success": False,
                    "error": "Không thể cập nhật đặt bàn với ngày trong quá khứ"
                }, status=400)
            form.save()
            return JsonResponse({"success": True, "message": "Cập nhật đặt bàn thành công!"}, status=200)
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    form = TableReservationForm(instance=reservation)
    return render(request, '/apps/web_01/modal/content/content_update_table_reservation.html', {
        'form': form,
        'reservation_id': id
    })
    
class TableReservationCreateForm(forms.ModelForm):
    class Meta:
        model = TableReservation
        fields = ['name', 'phone_number', 'many_person', 'table', 'date', 'hour']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'many_person': forms.NumberInput(attrs={'class': 'form-control'}),
            'table': forms.Select(attrs={'class': 'form-control'}),
        }

@require_POST
def create_table_reservation(request):
    """Tạo mới đặt bàn - Trả về JSON"""
    try:
        form = TableReservationCreateForm(request.POST)
        if form.is_valid():
            # Kiểm tra bàn có tồn tại không
            table = form.cleaned_data.get('table')
            if not table:
                return JsonResponse({
                    "success": False,
                    "error": "Bàn không tồn tại"
                }, status=404)

            # Kiểm tra bàn đã được đặt chưa
            date = form.cleaned_data.get('date')
            if date < current_date.today():
                return JsonResponse({
                    "success": False,
                    "error": "Không thể đặt bàn cho ngày trong quá khứ"
                }, status=400)
            hour = form.cleaned_data.get('hour')
            existing_reservation = TableReservation.objects.filter(
                table=table,
                date=date,
                hour=hour,
                status__in=['pending', 'confirmed']
            ).first()

            if existing_reservation:
                return JsonResponse({
                    "success": False,
                    "error": f"Bàn {table.table_number} đã được đặt vào {date.strftime('%d/%m/%Y')} lúc {hour.strftime('%H:%M')}"
                }, status=400)

            # Tạo đặt bàn mới
            reservation = form.save(commit=False)
            reservation.status = 'pending'  # Set trạng thái mặc định
            reservation.save()

            return JsonResponse({
                "success": True,
                "message": "Tạo đặt bàn thành công!",
                "data": {
                    "id": reservation.id,
                    "name": reservation.name,
                    "phone_number": reservation.phone_number,
                    "many_person": reservation.many_person,
                    "table": {
                        "id": reservation.table.id,
                        "table_number": reservation.table.table_number
                    },
                    "date": reservation.date.strftime('%Y-%m-%d'),
                    "hour": reservation.hour.strftime('%H:%M'),
                    "status": reservation.status,
                    "status_display": reservation.get_status_display(),
                    "created_at": reservation.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            }, status=201)
        else:
            return JsonResponse({
                "success": False,
                "error": "Dữ liệu không hợp lệ",
                "errors": form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Lỗi khi tạo đặt bàn: {str(e)}"
        }, status=500)


@require_POST
@login_required
def approve_table_reservation(request, id):
    try:
        reservation = get_object_or_404(TableReservation, id=id)
        reservation.status = 'confirmed'
        reservation.save()
        return JsonResponse({"success": True, "message": "Đặt bàn đã được xác nhận!"})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Lỗi: {str(e)}"}, status=400)


@require_POST
@login_required
def reject_table_reservation(request, id):
    try:
        reservation = get_object_or_404(TableReservation, id=id)
        reservation.status = 'cancelled'
        reservation.save()
        return JsonResponse({"success": True, "message": "Đặt bàn đã bị từ chối!"})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Lỗi: {str(e)}"}, status=400)

@require_POST
@login_required
def delete_table_reservation(request, id):
    try:
        reservation = get_object_or_404(TableReservation, id=id)
        reservation.delete()
        return JsonResponse({"success": True, "message": "Đã xóa đặt bàn!"})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Lỗi: {str(e)}"}, status=400)
