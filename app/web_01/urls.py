
from django.urls import path, include, re_path
from web_01 import views

app_name = "web_01"
# namespace
urlpatterns = [
    # WEB
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),

    path('management/', include([
        path('table/', include([
            path('list', views.TableManagementView.as_view(), name='table_list'),
            path('<int:id>/', views.edit_table, name='edit_table')
        ])),
        path('service/', include([
            path('list', views.ServiceManagementView.as_view(), name='service_list'),
            path('get-orders/', views.get_order_by_table, name='get_order_by_table'),
            path('order-payment/', views.order_payment, name='order_payment'),
        ])),
        path('order/', include([
             path('list', views.OrderManagementView.as_view(), name='order_list'),
             path('<int:id>/', views.detail_order, name='detail_order')

             ])),
        path('product/', include([
            path('list', views.ProductManagementView.as_view(), name='product_list'),
            path('create/', views.add_product, name='add_product'),
            path('import/', views.import_product, name='import_product'),
            path('<int:id>/', views.detail_product, name='detail_product')
        ])),

        path('customer/', include([
            path('list', views.CustomerManagementView.as_view(), name='customer_list'),
            # path('create/', views.add_product, name='add_product'),
            # path('import/', views.import_product, name='import_product'),
            # path('<int:id>/', views.detail_product, name='detail_product')
        ])),

        path('employee/', include([
            path('list', views.EmployeeManagementView.as_view(), name='employee_list'),
            # path('create/', views.add_product, name='add_product'),
            # path('import/', views.import_product, name='import_product'),
            # path('<int:id>/', views.detail_product, name='detail_product')
        ]))
    ]))
]
