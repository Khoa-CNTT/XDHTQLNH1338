from core.__Include_Library import *
from django.views.generic import TemplateView
from web_01.models import Ingredient, InventoryLog
from web_01.utils.utils import get_username

class InventoryManagementView(LoginRequiredMixin, TemplateView):
    template_name = '/apps/web_01/inventory/inventory_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        try:
            draw = int(request.POST.get("draw", 1))
            start = int(request.POST.get("start", 0))
            length = int(request.POST.get("length", 10))
            search_value = request.POST.get("search[value]", "").strip()

            # Queryset chính
            qs = Ingredient.objects.all()

            # Tìm kiếm (nếu có)
            if search_value:
                qs = qs.filter(
                    Q(name__icontains=search_value) |
                    Q(unit__icontains=search_value)
                )

            total_count = qs.count()
            qs = qs[start:start+length]

            data = []
            for index, ing in enumerate(qs):
                data.append({
                    'index': index,
                    'id': ing.id,
                    'name': ing.name,
                    'unit': ing.get_unit_display(),
                    'quantity': ing.quantity_in_stock,
                })

            return JsonResponse({
                "draw": draw,
                "recordsTotal": Ingredient.objects.count(),
                "recordsFiltered": total_count,
                "data": data
            }, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


def inventory_log_list(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    logs = ingredient.inventorylog_set.all().select_related('user').order_by('-last_updated')
    current_stock = ingredient.quantity_in_stock
    latest_log = logs.first()  # Log gần nhất
    return render(request, '/apps/web_01/modal/content/content_detail_inventory_log.html', {
        'ingredient': ingredient,
        'logs': logs,
        'current_stock': current_stock,  # Truyền vào template
        'latest_user': get_username(latest_log.user) if latest_log else '-'
    })


class IngredientImportForm(forms.Form):
    ingredient = forms.ModelChoiceField(queryset=Ingredient.objects.all(), label="Nguyên liệu")
    quantity = forms.IntegerField(min_value=1, label="Số lượng nhập")
    note = forms.CharField(required=False, widget=forms.Textarea, label="Ghi chú")


class IngredientImportForm(forms.ModelForm):
    class Meta:
        model = InventoryLog
        fields = ['ingredient', 'change', 'note']
        labels = {
            'ingredient': 'Nguyên liệu',
            'change': 'Số lượng nhập',
            'note': 'Ghi chú',
        }
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'change': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 1}),
            'note': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].queryset = Ingredient.objects.all()
        self.fields['change'].initial = 1


def import_ingredient(request):
    if request.method == 'POST':
        ingredient_ids = request.POST.getlist('ingredient[]')
        changes = request.POST.getlist('change[]')
        notes = request.POST.getlist('note[]')

        # ✅ Kiểm tra trùng nguyên liệu
        if len(ingredient_ids) != len(set(ingredient_ids)):
            return JsonResponse({'error': 'Không được nhập trùng nguyên liệu!'}, status=400)

        logs = []
        try:
            for i in range(len(ingredient_ids)):
                ing_id = int(ingredient_ids[i])
                change = int(changes[i])
                note = notes[i].strip()

                log = InventoryLog(
                    ingredient_id=ing_id,
                    change=change,
                    type='import',
                    note=note,
                    user=request.user  # thêm dòng này
                )
                log.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        ingredients = Ingredient.objects.all()
        return render(request, 'apps/web_01/modal/content/content_import_ingredient.html', {
            'ingredients': ingredients,
            'modal_id': 'importIngredientModal'
        })
