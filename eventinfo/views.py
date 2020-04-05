from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from django.contrib import messages
from django.utils import timezone

from eventinfo.models import Event, Event_types, Time_Slots, Tickets, Time_slot_status, Booking, Order_item, Order
from eventinfo.forms import EventSearchForm, ProfileForm, UserForm, BookingForm

import random
import string


def event_list(request):
    search_form = EventSearchForm(request.GET)
    events = Event.objects.all()
    if search_form.is_valid():
        events = events.filter(event_title__contains=search_form.cleaned_data['q'])
        if search_form.cleaned_data['event_type']:
            events = events.filter(event_type=search_form.cleaned_data['event_type'])
        # TODO: get time slots for every events
        '''
        if search_form.cleaned_data['sort']:
            if search_form.cleaned_data['sort'] == 'date-desc'
                events = events.order_by('event_')

        '''
    types = Event_types.objects.all()
    context = {
        'search_form': search_form,
        'events': events,
        'types': types,
    }

    return render(request, 'eventinfo/events.html', context)


def event_detail(request, event_id):
    booking_form = BookingForm(request.GET)
    event = get_object_or_404(Event, pk=event_id)
    guests = event.event_guests.all()
    time_slots = Time_Slots.objects.filter(event_id=event_id).order_by('event_start_date')
    tickets = Tickets.objects.filter(ticket_time_slot__event_id=event_id)
    time_slot_status = Time_slot_status(4)

    context = {
        'booking_form': booking_form,
        'guests': guests,
        'event': event,
        'time_slots': time_slots,
        'tickets': tickets,
        'time_slot_status': time_slot_status,
    }

    return render(request, 'eventinfo/event.html', context)


@login_required
def booking_tickets(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    time_slots = Time_Slots.objects.filter(event_id=event_id).order_by('event_start_date')
    tickets = Tickets.objects.filter(ticket_time_slot__event_id=event_id)
    time_slot_status = Time_slot_status(4)
    order_qs = Order.objects.filter(user=request.user, ordered=False, event=event)

    context = {
        'event': event,
        'time_slots': time_slots,
        'tickets': tickets,
        'time_slot_status': time_slot_status,
        'order_qs': order_qs,
    }

    if request.method == 'POST':
        i = 0
        tickets = []
        total_cost = 0
        try:
            for key, value in request.POST.items():
                if key.isdigit():

                    ticket = get_object_or_404(Tickets, pk=key)
                    seats = int(value)
                    assert ticket.ticket_status == ticket.SALE_OPEN, 'وضعیت'
                    assert ticket.get_free_seats() >= seats, 'ظرفیت {}'.format(ticket.id)
                    add_to_cart(request, ticket.id, seats)

        except Exception as e:
            context['error'] = str(e)
            return render(request, 'eventinfo/booking_tickets.html', context)
        else:
            return redirect("eventinfo:booking_checkout", event_id=event_id)

    return render(request, 'eventinfo/booking_tickets.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('eventinfo:event_list'))
        else:

            # TODO: LOAD ERROR MESSAGES IN POPUP FORM

            context = {
                'user': username,
                'error': False,
                'message': 'کاربری با این مشخصات یافت نشد.'
            }
            return render(request, 'eventinfo/account/login.html/', context)

    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('eventinfo:event_list'))
        else:
            context = {}

    return render(request, 'eventinfo/account/login.html/', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('eventinfo:event_list'))


@login_required
def account_profile(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, files=request.FILES, instance=request.user.profile)
        user_form = UserForm(request.POST, instance=request.user)
        try:
            profile_form.save() and user_form.save()
            context = {
                'user_form': user_form,
                'profile_form': profile_form,
                'message': 'پروفایل با موفقیت ویرایش شد.',
                'error': True
            }

        except:
            context = {
                'user_form': user_form,
                'profile_form': profile_form,
                'message': 'خطا در ویرایش اطلاعات',
                'error': False
            }

    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }

    return render(request, 'eventinfo/account/profile.html', context)


@login_required
def account_bookings(request):
    orders = Order.objects.filter(user=request.user)

    context = {
        'orders': orders
    }
    return render(request, 'eventinfo/account/dashboard-bookings.html', context)


@login_required
def account_invoice(request, ref_code):
    order = get_object_or_404(Order, ref_code=ref_code)
    if request.user == order.user:
        context = {
            'order': order
        }
    else:
        context = {

        }

    return render(request, 'eventinfo/account/dashboard-invoice.html', context)


def index(request):
    search_form = EventSearchForm(request.GET)
    events = Event.objects.all().order_by('-updated_at')
    event_type_list = events.values('event_type', 'event_type__type_title', 'event_type__type_icon').annotate(
        count=Count('event_type'))
    types = Event_types.objects.all()
    context = {
        'search_form': search_form,
        'event_type_list': event_type_list,
        'events': events,
        'types': types,
    }

    return render(request, 'eventinfo/index.html', context)


@login_required
def booking_confirmation(request, event_id):

    if request.method == 'POST':
        order = Order.objects.get(user=request.user, ordered=False)

        # TODO: booking model needs additional filed for changed user profile
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']
        email = request.POST['email']
        mobile = request.POST['mobile']

        context = {
            'order': order,
            'first_name': first_name,
        }

        try:
            assert request.user.profile.spend(order.get_total_cost()), 'موجودی حساب شما کافی نیست.'
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
                item.ticket.reserve_seats(item.seats)
            order.ordered = True
            # order.payment = payment
            order.ref_code = create_ref_code()
            ordered_date = timezone.now()
            order.ordered_date = ordered_date
            order.save()

        except Exception as e:
            context['error'] = str(e)

        return render(request, 'eventinfo/booking_confirmation.html', context)

    else:
        return redirect("eventinfo:index:")


@login_required
def add_to_cart(request, ticket_id, seats):
    ticket = get_object_or_404(Tickets, pk=ticket_id)
    event_id = ticket.ticket_time_slot.event_id.pk
    event = get_object_or_404(Event, pk=event_id)
    order_item, created = Order_item.objects.get_or_create(
        ticket=ticket,
        user=request.user,
        ordered=False,
        defaults={'seats': seats}
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        # TODO: check if all order have same event id
        if order.event == event:
            if order.items.filter(ticket_id=ticket.id).exists():
                order_item.seats = seats
                order_item.save()
                messages.info(request, "This item quantity was updated.")
            else:
                order.items.add(order_item)
                messages.info(request, "This item was added to your cart.")

        else:
            order.delete()
            order = Order.objects.create(user=request.user, event=event)
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")


    else:
        order = Order.objects.create(user=request.user, event=event)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")


@login_required
def booking_checkout(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    order = Order.objects.get(user=request.user, ordered=False)
    context = {
        'event': event,
        'order': order,
    }
    return render(request, 'eventinfo/booking_checkout.html', context)


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
