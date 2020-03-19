from django.urls import path
from eventinfo import views

app_name = 'eventinfo'

urlpatterns = [
    path('events/', views.event_list, name='event_list'),
    path('event/<int:event_id>', views.event_detail, name='event_detail'),
]
