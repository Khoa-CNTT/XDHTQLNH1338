from core.__Include_Library import *
from django.views.generic import TemplateView
from django import forms
from web_01.models import *
from django.db.models import Sum
import requests

from web_01.handle_view.table_view import (TableManagementView, edit_table)
from web_01.handle_view.order_view import (OrderManagementView, detail_order)
from web_01.handle_view.product_view import (ProductManagementView, add_product, import_product, detail_product, best_seller)
from web_01.handle_view.service_view import (ServiceManagementView, get_order_by_table, complete_payment, get_product_service,
                                             complete_payment_multi_order, update_item_status, end_session, add_product_to_order)
from web_01.handle_view.customer_view import (CustomerManagementView)
from web_01.handle_view.employee_view import (EmployeeManagementView)
from web_01.handle_view.table_reservation_view import (TableReservationManagementView)
from web_01.handle_view.inventory_view import (InventoryManagementView, inventory_log_list, import_ingredient)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/web_01/dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Tổng số thực đơn
        context['total_products'] = Product.objects.count()

        # Tổng doanh thu
        context['total_revenue'] = (
            OrderDetail.objects.aggregate(total=Sum('total'))['total'] or 0
        )

        # Tổng số đơn đặt hàng
        context['total_orders'] = Order.objects.count()

        # Tổng số khách hàng
        context['total_customers'] = Customer.objects.count()

        return context


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


API_KEY = 'AIzaSyB9-HJ7Gg7P6Dm2PSadDPpa-u7i_lkb8A8'

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        message = request.POST.get("message", "")
        prompt = f"Bạn là trợ lý quản lý nhà hàng. {message}"

        try:
            # Gửi yêu cầu đến API Gemini
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",  # Đảm bảo URL đúng
                headers={"Content-Type": "application/json"},
                params={"key": API_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}]}
            )

            # Kiểm tra mã trạng thái HTTP
            if response.status_code != 200:
                print(f"Error response: {response.status_code}")
                print(f"Response content: {response.text}")
                return JsonResponse({"reply": "⚠️ Lỗi khi kết nối đến chatbot. Vui lòng thử lại."})

            # Chuyển đổi phản hồi thành JSON
            try:
                result = response.json()
                print("Gemini response:", result)

                # Xử lý phản hồi từ Gemini API
                reply = (
                    result.get("candidates", [{}])[0]
                          .get("content", {})
                          .get("parts", [{}])[0]
                          .get("text", "Không có phản hồi từ chatbot.")
                )

                # Lưu lịch sử trò chuyện vào cơ sở dữ liệu
                ChatHistory.objects.create(
                    user_message=message,
                    bot_reply=reply
                )

            except ValueError:
                print("Lỗi parse JSON:", response.text)
                reply = "⚠️ Lỗi khi nhận dữ liệu từ chatbot."

        except Exception as e:
            print("Lỗi gọi API Gemini:", str(e))
            reply = "⚠️ Lỗi khi kết nối đến chatbot. Vui lòng thử lại."

        return JsonResponse({"reply": reply})

@csrf_exempt
def get_chat_history(request):
    history = ChatHistory.objects.all().order_by('-created_at')[:10]  # Lấy 10 tin nhắn gần nhất
    chat_history = [{"user_message": h.user_message, "bot_reply": h.bot_reply, "created_at": h.created_at} for h in history]
    return JsonResponse({"chat_history": chat_history})