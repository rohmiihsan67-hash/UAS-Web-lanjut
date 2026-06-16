from django.contrib import admin
from django.urls import path, include
from akun import views as akun_views

urlpatterns = [
    path('', akun_views.home_view, name='home'),
    path('admin/', admin.site.urls),
    path('akun/', include('akun.urls')),
    path('user/', include('user.urls')),
    path('accounts/', include('allauth.urls')),  # Google OAuth routes
]
