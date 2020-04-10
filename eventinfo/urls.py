from django.urls import path
from eventinfo import views

app_name = 'eventinfo'

urlpatterns = [
    path('', views.index, name='index'),
    path('organizer/<int:organizer_id>/', views.organizer_profile, name='organizer_profile'),
    path('events/', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/booking/tickets/', views.booking_tickets, name='booking_tickets'),
    path('event/<int:event_id>/booking/checkout/', views.booking_checkout, name='booking_checkout'),
    path('event/<int:event_id>/booking/confirmation/', views.booking_confirmation, name='booking_confirmation'),

    path('account/', views.account_dashboard, name='account_dashboard'),
    #path('account/signup/', views.signup, name='signup'),
    path('account/login/', views.login_view, name='login'),
    path('account/logout/', views.logout_view, name='logout'),
    path('account/profile/', views.account_profile, name='account_profile'),
    path('account/bookings/', views.account_bookings, name='account_bookings'),
    path('account/invoice/<str:ref_code>/', views.account_invoice, name='account_invoice'),

    path('bookmark/', views.bookmark_toggle, name='bookmark_toggle')

]
