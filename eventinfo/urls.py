from django.urls import path, re_path
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

    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            views.activate, name='activate'),
    path('account/', views.account_dashboard, name='account_dashboard'),
    path('account/login/', views.login_view, name='login'),
    path('account/logout/', views.logout_view, name='logout'),
    path('account/reset_password', views.reset_password, name="reset_password"),
    re_path(r'^account/reset_password_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.reset_password_confirm, name='reset_password_confirm'),
    path('account/profile/', views.account_profile, name='account_profile'),
    path('account/bookings/', views.account_bookings, name='account_bookings'),
    path('account/bookmarks/', views.account_bookmarks, name='account_bookmarks'),
    path('account/invoice/<str:ref_code>/', views.account_invoice, name='account_invoice'),

    path('bookmark/', views.bookmark_toggle, name='bookmark_toggle'),
    path('remove-card/', views.remove_card, name='remove-card'),

    path('terms/', views.terms, name='terms'),
    path('contact/', views.contact, name='contact'),

]
