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
]
