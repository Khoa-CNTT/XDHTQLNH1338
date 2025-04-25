from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from django.db.models import Q
from web_01.models import TableReservation, Table

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
            order_dir = request.POST.get("order[0][dir]", "asc")
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
