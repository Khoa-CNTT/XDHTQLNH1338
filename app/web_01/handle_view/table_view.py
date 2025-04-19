
from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from web_01.models import Table
from django import forms
from django.contrib.auth.decorators import login_required


class TableManagementView(LoginRequiredMixin, TemplateView):
    template_name = '/apps/web_01/table/table_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, **kwargs):
        try:
            params = json.loads(request.POST.get('params', '{}'))
            table_list = Table.objects.all()

            context = self.get_context_data(**kwargs)

            context['table_list'] = table_list

            return render(
                request,
                '/apps/web_01/table/table_content.html',
                context
            )

        except json.JSONDecodeError:
            return HttpResponse(0)


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['status']  # Danh sách các trường cần nhập
        widgets = {
            'table_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Số bàn', 'disabled': 'disabled'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'qr_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


@login_required
def edit_table(request, id):
    """Xử lý chỉnh sửa bàn bằng AJAX"""
    table = get_object_or_404(Table, id=id)

    if request.method == "POST":
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "message": "Cập nhật thành công!"}, status=200)
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    # Nếu không phải POST request, render form như bình thường
    form = TableForm(instance=table)
    return render(request, 'apps/web_01/modal/content/content_edit_table.html', {'form': form, 'table_id': id})
