import os
from web_01.models import Product, Category, Ingredient, IngredientProduct
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import cloudinary.uploader
import requests
import pandas as pd
from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from web_01.models import Product, IngredientProduct, Ingredient
from django.forms import inlineformset_factory
from web_01.utils.model_consts import CATEGORY_STATUS_CHOICES


class ProductManagementView(LoginRequiredMixin, TemplateView):
    template_name = '/apps/web_01/product/product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.filter(status='active').values_list('id', 'name')
        context['price_list'] = [
            ('10000-50000', '10.000đ -> 50.000'),
            ('50000-100000', '50.000đ -> 100.000'),
            ('100000-150000', '100.000đ -> 150.000'),
            ('150000-200000', '150.000đ -> 200.000'),
        ]
        return context

    def post(self, request, *args, **kwargs):
        try:
            draw = int(request.POST.get("draw", 1))
            start = int(request.POST.get("start", 0))
            length = int(request.POST.get("length", 10))
            search_value = request.POST.get("search[value]", "").strip()
            # Lấy dữ liệu từ request
            category = request.POST.get("category", "[]")  # Nếu không có, mặc định là []
            price = request.POST.get("price", "-1")
            print('category', category)
            category_ids = json.loads(category)  # Chuyển từ JSON thành danh sách Python

            order_column_index = int(request.POST.get("order[0][column]", 0))
            order_dir = request.POST.get("order[0][dir]", "asc")

            column_mapping = {
                0: "id",
                1: "name",
                2: "image",
                3: "category__name",
                4: "price"
            }

            # Kiểm tra nếu index không hợp lệ
            if order_column_index not in column_mapping:
                order_column_index = 0

            order_column = column_mapping[order_column_index]

            # Sắp xếp theo thứ tự ASC/DESC
            if order_dir == "desc":
                order_column = "-" + order_column

            # Query sản phẩm từ database
            product_list = Product.objects.select_related("category")

            filter_dict = dict()
            if category_ids:
                filter_dict['category_id__in'] = category_ids

            if search_value:
                filter_dict['name__icontains'] = search_value

            if price != "-1":
                min_price, max_price = price.split('-')
                filter_dict['price__gte'] = int(min_price)
                filter_dict['price__lte'] = int(max_price)

            product_list = product_list.filter(**filter_dict).order_by(order_column)
            total_count = product_list.count()
            product_list = product_list[start: start + length]  # Sort + Pagination

            # Chuẩn bị dữ liệu JSON
            products_data = [
                {
                    "index": index + 1,
                    "id": product.id,
                    "name": product.name,
                    "image": product.image.url if product.image else None,
                    "category": product.category.name if product.category else "Không có danh mục",
                    "price": f"{product.price:,} VND",
                }
                for index, product in enumerate(product_list, start=start)
            ]

            return JsonResponse({
                "draw": draw,
                "recordsTotal": total_count,
                "recordsFiltered": total_count,
                "data": products_data
            }, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class IngredientProductForm(forms.ModelForm):
    class Meta:
        model = IngredientProduct
        fields = ['ingredient', 'quantity_required']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'quantity_required': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '1'}),
        }


IngredientProductFormSet = inlineformset_factory(
    Product, IngredientProduct,
    form=IngredientProductForm,
    extra=1,  # Số lượng nguyên liệu mặc định hiển thị
    can_delete=True  # Cho phép xóa nguyên liệu khỏi sản phẩm
)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'category': forms.Select(attrs={'id': 'category-select', 'class': 'form-control form-control-sm-'}),
            'price': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
            'image': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'accept': 'image/jpeg,image/png'}),
        }


@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        print('form', form)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "message": "Thêm sản phẩm thành công!"}, status=200)
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = ProductForm()

    return render(request, 'apps/web_01/modal/content/content_add_product.html', {'form': form})


@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        # Lấy danh sách nguyên liệu + số lượng từ request
        ingredient_data = json.loads(request.POST.get('ingredients', '[]'))  # [{id: 1, quantity: 2}, ...]

        if form.is_valid():
            product = form.save()

            # Xóa nguyên liệu cũ (nếu có)
            IngredientProduct.objects.filter(product=product).delete()

            # Lưu mới nguyên liệu kèm số lượng
            for item in ingredient_data:
                ingredient_id = item.get('id')
                quantity = item.get('quantity', 1)

                if ingredient_id:
                    ingredient = Ingredient.objects.get(id=ingredient_id)
                    IngredientProduct.objects.create(
                        product=product,
                        ingredient=ingredient,
                        quantity_required=quantity
                    )

            return JsonResponse({"success": True, "message": "Thêm sản phẩm thành công!"}, status=200)

        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    else:
        form = ProductForm()
        ingredients = Ingredient.objects.all()  # Lấy danh sách nguyên liệu

    return render(request, 'apps/web_01/modal/content/content_add_product.html', {
        'form': form,
        'ingredients': ingredients
    })


@login_required
def import_product(request):
    if request.method == "POST" and request.FILES.get("excelFile"):
        file = request.FILES["excelFile"]
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)

        # Lưu file Excel vào thư mục media
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Đọc file Excel
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Lỗi khi đọc file Excel: {e}"})

        # Lặp qua từng dòng trong file Excel
        for index, row in df.iterrows():
            try:
                product_name = row["Tên sản phẩm"]
                description = row.get("Mô tả", "")
                price = row.get("Giá", 0)
                image_url = row.get("Ảnh", "").strip()
                category_name = row.get("Danh mục", "").strip()
                ingredients_data = row.get("Nguyên liệu", "")

                # Xử lý danh mục
                category = None
                if category_name:
                    category, _ = Category.objects.get_or_create(name=category_name)

                # Tải ảnh lên Cloudinary
                image_cloud_url = None
                if image_url:
                    try:
                        uploaded_image = cloudinary.uploader.upload(image_url)
                        image_cloud_url = uploaded_image.get("secure_url")
                    except Exception as e:
                        print(f"❌ Lỗi khi tải ảnh từ {image_url}: {e}")

                # Tạo hoặc cập nhật sản phẩm
                product, created = Product.objects.update_or_create(
                    name=product_name,
                    defaults={
                        "description": description,
                        "price": price,
                        "image": image_cloud_url,
                        "category": category,
                    },
                )

                # Xóa nguyên liệu cũ
                IngredientProduct.objects.filter(product=product).delete()

                # Thêm nguyên liệu mới
                if ingredients_data and isinstance(ingredients_data, str):
                    for item in ingredients_data.split(","):
                        try:
                            ingredient_id, quantity = map(str.strip, item.split(":"))
                            ingredient = Ingredient.objects.get(id=int(ingredient_id))
                            IngredientProduct.objects.create(
                                product=product, ingredient=ingredient, quantity_required=int(quantity)
                            )
                        except Exception as e:
                            print(f"❌ Lỗi thêm nguyên liệu cho {product_name}: {e}")

            except Exception as e:
                print(f"❌ Lỗi khi xử lý dòng {index + 1}: {e}")

        # Xóa file đã nhập
        if os.path.exists(file_path):
            os.remove(file_path)
        return JsonResponse({"success": True, "message": "Nhập sản phẩm thành công!"})

    return render(request, 'apps/web_01/modal/content/content_import_product.html', {})


@login_required
def detail_product(request, id):
    product = get_object_or_404(Product.objects.select_related("category"), id=id)
    ingredients = IngredientProduct.objects.filter(product=product).select_related("ingredient")

    context = {
        "product": product,
        "ingredients": ingredients
    }
    return render(request, "apps/web_01/modal/content/content_detail_product.html", context)
