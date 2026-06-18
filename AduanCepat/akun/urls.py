from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/update-status/<int:report_id>/', views.admin_update_status, name='admin_update_status'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('reset-success/', views.reset_success_view, name='reset_success'),
    path('admin-dashboard/block-ip/', views.block_ip, name='block_ip'),
    path('admin-dashboard/unblock-ip/<int:ip_id>/', views.unblock_ip, name='unblock_ip'),
    path('admin-dashboard/save-settings/', views.save_settings, name='save_settings'),
    path('admin-dashboard/clear-cache/', views.clear_cache, name='clear_cache'),
    path('admin-dashboard/security-logs-partial/', views.admin_security_logs_partial, name='admin_security_logs_partial'),
]
