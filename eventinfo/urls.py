from django.urls import path
from eventinfo import views

app_name = 'eventinfo'

urlpatterns = [
    path('events/', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/booking/', views.event_booking, name='event_booking'),
    path('account/login/', views.login_view, name='login'),
    path('account/logout/', views.logout_view, name='logout'),
    path('account/profile', views.account_profile, name='account_profile')
]
