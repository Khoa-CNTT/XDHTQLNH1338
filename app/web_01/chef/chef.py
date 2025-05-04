from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from web_01.models import Order, OrderDetail, Product, Ingredient
from web_01.chef.decorators import chef_required
import json


@login_required
@chef_required
def chef_dashboard(request):
    """Hiển thị dashboard cho đầu bếp"""
    # Lấy các đơn hàng đang chờ xử lý và đang thực hiện
    pending_orders = OrderDetail.objects.filter(
        status='pending',
        is_deleted=False
    ).select_related('order', 'product').order_by('created_at')

    in_progress_orders = OrderDetail.objects.filter(
        status='in_progress',
    ).select_related('order', 'product').order_by('created_at')

    completed_orders = OrderDetail.objects.filter(
        status='completed',
        updated_at__gte=timezone.now().replace(hour=0, minute=0, second=0)
    ).select_related('order', 'product').order_by('-updated_at')[:10]

    # Lấy danh sách món ăn phổ biến
    popular_dishes = Product.objects.filter(
    )[:10]

    # Kiểm tra nguyên liệu sắp hết
    low_stock_ingredients = Ingredient.objects.filter(
        quantity_in_stock__lte=50,
    ).order_by('quantity_in_stock')

    context = {
        'pending_orders': pending_orders,
        'in_progress_orders': in_progress_orders,
        'completed_orders': completed_orders,
        'popular_dishes': popular_dishes,
        'low_stock_ingredients': low_stock_ingredients,
    }

    return render(request, '/apps/web_01/dashboard/chef_dashboard.html', context)


# @login_required
# @chef_required
# def check_new_orders(request):
#     """Kiểm tra đơn hàng mới"""
#     # Lấy thời gian hiện tại trừ đi 1 phút
#     one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)

#     # Tìm các đơn hàng mới trong 1 phút qua
#     new_orders = OrderDetail.objects.filter(
#         status='pending',
#         is_deleted=False,
#         created_at__gte=one_minute_ago
#     ).values('id', 'product__name', 'order__table__table_number')

#     return JsonResponse({
#         'status': 'success',
#         'new_orders': list(new_orders)
#     })


# @login_required
# @chef_required
# def order_details(request, order_id):
#     """Hiển thị chi tiết đơn hàng cho đầu bếp"""
#     order = get_object_or_404(Order, id=order_id, is_deleted=False)
#     order_details = OrderDetail.objects.filter(
#         order=order,
#         is_deleted=False
#     ).select_related('product')

#     context = {
#         'order': order,
#         'order_details': order_details,
#     }

#     return render(request, 'apps/web_01/chef/order_details.html', context)


# @login_required
# @chef_required
# def update_order_status(request):
#     """Cập nhật trạng thái món ăn"""
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             order_detail_id = data.get('order_detail_id')
#             new_status = data.get('status')

#             if not order_detail_id or not new_status:
#                 return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin cần thiết'})

#             # Kiểm tra trạng thái hợp lệ
#             valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
#             if new_status not in valid_statuses:
#                 return JsonResponse({'status': 'error', 'message': 'Trạng thái không hợp lệ'})

#             # Cập nhật trạng thái
#             order_detail = get_object_or_404(OrderDetail, id=order_detail_id, is_deleted=False)
#             order_detail.status = new_status
#             order_detail.updated_at = timezone.now()

#             # Nếu hoàn thành, cập nhật thời gian hoàn thành
#             if new_status == 'completed':
#                 order_detail.completed_at = timezone.now()

#                 # Cập nhật số lượng nguyên liệu
#                 for ingredient_product in order_detail.product.ingredientproduct_set.all():
#                     ingredient = ingredient_product.ingredient
#                     quantity_used = ingredient_product.quantity * order_detail.quantity

#                     # Trừ số lượng nguyên liệu đã sử dụng
#                     ingredient.quantity_in_stock -= quantity_used
#                     ingredient.save()

#                     # Ghi log nhập xuất kho
#                     from web_01.models import InventoryLog
#                     InventoryLog.objects.create(
#                         ingredient=ingredient,
#                         change=-quantity_used,
#                         reason=f"Sử dụng cho món {order_detail.product.name} (Đơn hàng #{order_detail.order.id})"
#                     )

#             order_detail.save()

#             # Kiểm tra nếu tất cả các món trong đơn hàng đã hoàn thành
#             all_completed = True
#             for detail in OrderDetail.objects.filter(order=order_detail.order, is_deleted=False):
#                 if detail.status != 'completed' and detail.status != 'cancelled':
#                     all_completed = False
#                     break

#             # Nếu tất cả đã hoàn thành, cập nhật trạng thái đơn hàng
#             if all_completed:
#                 order_detail.order.status = 'completed'
#                 order_detail.order.completed_at = timezone.now()
#                 order_detail.order.save()

#             return JsonResponse({
#                 'status': 'success',
#                 'message': 'Cập nhật trạng thái thành công',
#                 'order_detail': {
#                     'id': order_detail.id,
#                     'status': order_detail.status,
#                     'updated_at': order_detail.updated_at.strftime('%H:%M:%S')
#                 }
#             })

#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)})

#     return JsonResponse({'status': 'error', 'message': 'Phương thức không được hỗ trợ'})


# @login_required
# @chef_required
# def recipe_view(request, product_id):
#     """Hiển thị công thức nấu ăn cho món ăn"""
#     product = get_object_or_404(Product, id=product_id, is_deleted=False)

#     # Lấy danh sách nguyên liệu
#     ingredients = product.ingredientproduct_set.all().select_related('ingredient')

#     context = {
#         'product': product,
#         'ingredients': ingredients,
#     }

#     return render(request, 'apps/web_01/chef/recipe.html', context)


# @login_required
# @chef_required
# def search_dishes(request):
#     """Tìm kiếm món ăn"""
#     query = request.GET.get('q', '')

#     if query:
#         products = Product.objects.filter(
#             Q(name__icontains=query) | Q(description__icontains=query),
#             is_deleted=False,
#             category__type='food'
#         ).order_by('name')
#     else:
#         products = Product.objects.filter(
#             is_deleted=False,
#             category__type='food'
#         ).order_by('-order_count')[:20]

#     context = {
#         'products': products,
#         'query': query
#     }

#     return render(request, 'apps/web_01/chef/search_dishes.html', context)
