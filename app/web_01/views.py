from core.__Include_Library import *
from django.views.generic import TemplateView
from django import forms
from web_01.models import *
from django.db.models import Sum, Count, F, Prefetch
from django.utils.decorators import method_decorator
import requests
from django.conf import settings
from web_01.analyzer import analyze_message, handle_intent

from web_01.handle_view.table_view import (TableManagementView, edit_table, add_table, table_qr,table_create)
from web_01.handle_view.order_view import (OrderManagementView, detail_order, detail_invoice)
from web_01.handle_view.product_view import (ProductManagementView, add_product, import_product, detail_product, best_seller)
from web_01.handle_view.service_view import (ServiceManagementView, get_order_by_table, complete_payment, get_product_service,
                                             complete_payment_multi_order, update_item_status, end_session, add_product_to_order)
from web_01.handle_view.customer_view import (CustomerManagementView)
from web_01.handle_view.employee_view import (EmployeeManagementView)
from web_01.handle_view.table_reservation_view import (TableReservationManagementView)
from web_01.handle_view.inventory_view import (InventoryManagementView, inventory_log_list, import_ingredient)
from web_01.decorator import admin_required

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


# @method_decorator(admin_required, name='dispatch')
# class DashboardView(LoginRequiredMixin, TemplateView):
#     template_name = 'apps/web_01/dashboard/dashboard.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         # Tổng số thực đơn
#         context['total_products'] = Product.objects.count()

#         # Tổng doanh thu
#         context['total_revenue'] = (
#             OrderDetail.objects.aggregate(total=Sum('total'))['total'] or 0
#         )

#         # Tổng số đơn đặt hàng
#         context['total_invoice'] = Invoice.objects.count()

#         # Tổng số khách hàng
#         context['total_customers'] = Customer.objects.count()

#         return context


@admin_required
def dashboard(request):
    """Dashboard chính hiển thị thông tin tổng quan"""
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    # Thống kê đơn hàng hôm nay
    total_orders_today = Order.objects.filter(
        created_at__date=today,
        is_deleted=False
    ).count()

    # Doanh thu hôm nay
    revenue_today = Invoice.objects.filter(
        created_at__date=today,
        is_deleted=False
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Doanh thu tháng này
    revenue_month = Invoice.objects.filter(
        created_at__date__gte=start_of_month,
        is_deleted=False
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Sản phẩm bán chạy
    best_selling = OrderDetail.objects.filter(
        is_deleted=False
    ).values('product__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    # Tình trạng bàn
    tables_status = {
        'available': Table.objects.filter(status='available').count(),
        'occupied': Table.objects.filter(status='occupied').count(),
        'reserved': Table.objects.filter(status='reserved').count(),
    }

    # Danh sách bàn có thông tin session hiện tại (nếu có)
    active_sessions = Session.objects.filter(status='active')
    tables = Table.objects.prefetch_related(
        Prefetch('session_set', queryset=active_sessions, to_attr='active_sessions')
    )

    for table in tables:
        current_session = table.active_sessions[0] if table.active_sessions else None
        table.current_session = current_session
        table.total_amount = current_session.total_amount if current_session else 0
    # Cảnh báo tồn kho
    low_stock_items = Ingredient.objects.filter(quantity_in_stock__lte=50).order_by('quantity_in_stock')[:5]

    # Dữ liệu cho biểu đồ doanh thu theo ngày (7 ngày gần nhất)
    revenue_by_day = []
    day_labels = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_revenue = Invoice.objects.filter(
            created_at__date=day,
            is_deleted=False
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        revenue_by_day.append(day_revenue)
        day_labels.append(day.strftime('%d/%m'))

    # Dữ liệu cho biểu đồ doanh thu theo danh mục
    revenue_by_category = OrderDetail.objects.filter(
        is_deleted=False,
        created_at__date__gte=start_of_month
    ).values('product__category__name').annotate(
        total=Sum(F('price') * F('quantity'))
    ).order_by('-total')[:5]

    # Dữ liệu cho biểu đồ tỷ lệ đơn hàng theo trạng thái
    order_status_counts = Order.objects.filter(
        is_deleted=False
    ).values('status').annotate(
        count=Count('id')
    )

    # Dữ liệu cho biểu đồ tồn kho nguyên liệu (10 nguyên liệu có tỷ lệ sử dụng cao nhất)
    top_ingredients = Ingredient.objects.annotate(
        usage_count=Count('ingredientproduct')
    ).order_by('-usage_count')[:10]

    ingredient_labels = [ing.name for ing in top_ingredients]
    ingredient_stocks = [ing.quantity_in_stock for ing in top_ingredients]

    # Thêm dữ liệu vào context
    context = {
        'total_orders_today': total_orders_today,
        'revenue_today': revenue_today,
        'revenue_month': revenue_month,
        'best_selling': best_selling,
        'tables_status': tables_status,
        'low_stock_items': low_stock_items,
        'tables': tables,
        'revenue_by_day': revenue_by_day,
        'day_labels': day_labels,
        'revenue_by_category': revenue_by_category,
        'order_status_counts': order_status_counts,
        'ingredient_labels': ingredient_labels,
        'ingredient_stocks': ingredient_stocks,
    }

    return render(request, 'apps/web_01/dashboard/dashboard_2.html', context)


class CustomLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class CustomLoginView(FormView):
    template_name = 'base/login.html'
    form_class = CustomLoginForm
    success_url = '/'  # Trang sau khi đăng nhập thành công

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        # Tìm user qua email
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            form.add_error('username', 'Username không tồn tại!')
            return self.form_invalid(form)

        # Xác thực user
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            if hasattr(user, 'employee'):
                if user.employee.role == 'chef':
                    return redirect(reverse('web_01:chef_dashboard'))  # Redirect tới trang đầu bếp
                if user.employee.role == 'staff':
                    return redirect(reverse('web_01:service_list'))
            return redirect(self.get_success_url())

        else:
            form.add_error('password', 'Mật khẩu không đúng!')
            return self.form_invalid(form)


def logout_view(request):
    logout(request)
    return redirect(reverse_lazy('web_01:login'))


@login_required
def get_notification(request):
    notifications = Notification.objects.all()

    notification_html = render_to_string('apps/web_01/commom/notifcation.html', {"notifications": notifications})
    notification_len = notifications.count()

    return JsonResponse({
        'notification_html': notification_html,  # ✅ sửa key ở đây
        'notification_len': notification_len,
    })


def call_gemini(prompt):
    try:
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "key": settings.GEMINI_API_KEY
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)

        if response.status_code == 200:
            result = response.json()
            # Trích xuất phần trả lời
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return reply.strip()
        else:
            print("Gemini API lỗi:", response.text)
            return "Tôi đang bận, vui lòng thử lại sau."

    except Exception as e:
        print("Lỗi call_gemini:", str(e))
        return "Lỗi nội bộ khi gọi Gemini."


def get_recent_messages(limit=5):
    history = ChatHistory.objects.order_by('-created_at')[:limit]
    return [f"User: {h.user_message}\nBot: {h.bot_reply}" for h in history]


@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        message = request.POST.get("message", "")
        prompt = f"Bạn là trợ lý quản lý nhà hàng. {message}"

        try:
            # 1. Phân tích intent
            intent_data = analyze_message(message)
            print('intent_data', intent_data)
            if intent_data:
                reply = handle_intent(intent_data)
            else:
                # Nếu không nhận ra, fallback Gemini
                history = get_recent_messages()
                prompt = "\n".join(history) + f"\nUser: {message}\nBot:"
                reply = call_gemini(prompt)

            # Lưu lịch sử
            ChatHistory.objects.create(
                user_message=message,
                bot_reply=reply
            )

        except Exception as e:
            reply = "Lỗi nội bộ khi xử lý yêu cầu."

        return JsonResponse({"reply": reply})


@csrf_exempt
def get_chat_history(request):
    history = ChatHistory.objects.all().order_by('-created_at')[:10]  # Lấy 10 tin nhắn gần nhất
    chat_history = [{"user_message": h.user_message, "bot_reply": h.bot_reply, "created_at": h.created_at} for h in history]
    return JsonResponse({"chat_history": chat_history})
