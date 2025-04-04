from core.__Include_Library import *
from django.views.generic import TemplateView
from django import forms


from web_01.handle_view.table_view import (TableManagementView, edit_table)
from web_01.handle_view.order_view import (OrderManagementView, detail_order)
from web_01.handle_view.product_view import (ProductManagementView, add_product, import_product, detail_product)
from web_01.handle_view.service_view import (ServiceManagementView, get_order_by_table, complete_payment, get_product_service)
from web_01.handle_view.customer_view import (CustomerManagementView)
from web_01.handle_view.employee_view import (EmployeeManagementView)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = '/apps/web_01/dashboard.html'


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
