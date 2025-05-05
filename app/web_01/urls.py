
from django.urls import path, include, re_path
from web_01 import views
from web_01.chatbot import chatbot_view
from web_01.chef import chef
app_name = "web_01"

# namespace
urlpatterns = [
    # WEB
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('chef/', chef.chef_dashboard, name='chef_dashboard'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path("chatbot/", chatbot_view.chatbot_api, name="chatbot_api"),
    path("get-chat-history/", views.get_chat_history, name="get_chat_history"),
    path('get-notifications', views.get_notification, name='get_notification'),


    path('management/', include([
        path('table/', include([
            path('list', views.TableManagementView.as_view(), name='table_list'),
            path('<int:id>/', views.edit_table, name='edit_table'),
            # path('add', views.add_table, name='add_table'),
            path('<int:table_id>/qr/', views.table_qr, name='manager_table_qr'),
            path('create', views.table_create, name='manager_table_create'),
        ])),
        path('service/', include([
            path('list', views.service_dashboard, name='service_list'),
            path('get-orders/', views.get_order_by_table, name='get_order_by_table'),
            path('get-product-service/', views.get_product_service, name='get_product_service'),
            path('complete-payment/', views.complete_payment, name='complete_payment'),
            path('complete-payment-multi-order/', views.complete_payment_multi_order, name='complete_payment_multi_order'),
            path('update-item-status/', views.update_item_status, name='update_item_status'),
            path('end-session/', views.end_session, name='end_session'),
            path('add-product-to-order/', views.add_product_to_order, name='add_product_to_order'),])),
        path('order/', include([
             path('list', views.OrderManagementView.as_view(), name='order_list'),
             #  path('<int:id>/', views.detail_order, name='detail_order'),
             path('<int:id>/', views.detail_invoice, name='detail_invoice')

             ])),
        path('product/', include([
            path('list', views.ProductManagementView.as_view(), name='product_list'),
            path('create/', views.add_product, name='add_product'),
            path('import/', views.import_product, name='import_product'),
            path('<int:id>/', views.detail_product, name='detail_product'),
            path('best-seller/', views.best_seller, name='best_seller'),

        ])),

        path('customer/', include([
            path('list', views.CustomerManagementView.as_view(), name='customer_list'),
        ])),

        path('employee/', include([
            path('list', views.EmployeeManagementView.as_view(), name='employee_list'),
        ])),

        path('table-reservation/', include([
            path('list', views.TableReservationManagementView.as_view(), name='table_reservation_list'),
        ])),



        path('inventory/', views.InventoryManagementView.as_view(), name='inventory_list'),
        path('inventory/log/<int:ingredient_id>/', views.inventory_log_list, name='inventory_log_list'),
        path('inventory/import/', views.import_ingredient, name='import_ingredient'),
        path('inventory/export/', views.export_ingredient, name='export_ingredient'),
        path('inventory/add/', views.add_ingredient, name='add_ingredient'),
        path('inventory/request/', views.ingredient_request, name='ingredient_request'),
        path('inventory/dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
        path('inventory/dashboard-stats/', views.inventory_dashboard_stats, name='inventory_dashboard_stats'),
        path('inventory/report/', views.inventory_report, name='inventory_report'),

    ]))
]
