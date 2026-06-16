from django.urls import path
from . import views

urlpatterns = [
    path('', views.overview_view, name='user_overview'),
    path('overview/', views.overview_view, name='user_overview'),
    path('incident-map/', views.incident_map_view, name='user_incident_map'),
    path('public-feed/', views.public_feed_view, name='user_public_feed'),
    path('my-submissions/', views.my_submissions_view, name='user_my_submissions'),
    path('profile/', views.profile_view, name='user_profile'),
    path('settings/', views.settings_view, name='user_settings'),
    path('new-report/', views.new_report_view, name='user_new_report'),
]
