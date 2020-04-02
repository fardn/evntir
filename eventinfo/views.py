from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from eventinfo.models import Event, Event_types, Time_Slots, Tickets, Time_slot_status, Booking
from eventinfo.forms import EventSearchForm, ProfileForm, UserForm, BookingForm


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

    context = {
        'event': event,
        'time_slots': time_slots,
        'tickets': tickets,
        'time_slot_status': time_slot_status,
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
                    total_cost += ticket.ticket_price * seats
                    item = {
                        'ticket': ticket,
                        'seats': seats,
                    }
                    tickets.append(item)
                    i += 1

        except Exception as e:
            context['error'] = str(e)
            return render(request, 'eventinfo/booking_tickets.html', context)

        else:
            context = {
                'event': event,
                'tickets': tickets,
                'total_cost': total_cost,
            }
            return render(request, 'eventinfo/booking_detail.html', context)

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
        i = 0
        tickets = []
        total_cost = 0
        for key, value in request.POST.items():
            if key.isdigit():
                ticket = get_object_or_404(Tickets, pk=key)
                seats = value
                total_cost += int(ticket.ticket_price) * int(seats)
                item = {
                    'ticket': ticket,
                    'seats': seats,
                }
                tickets.append(item)
                i += 1

        first_name = request.POST['first-name']
        last_name = request.POST['last-name']
        email = request.POST['email']
        mobile = request.POST['mobile']
        book_number = 123

        context = {
            'tickets': tickets,
            'first_name': first_name,
        }

        try:
            assert int(total_cost) <= int(request.user.profile.balance), 'حساب'
            for ticket in tickets:
                assert ticket['ticket'].ticket_status == ticket['ticket'].SALE_OPEN, 'وضعیت'
                free_seats = ticket['ticket'].get_free_seats
                assert 25 >= int(ticket['seats']), 'ظرفیت'
                Booking.objects.create(book_number=book_number, book_user=request.user, book_ticket=ticket['ticket'],
                                       book_seats=ticket['seats'], book_total_cost=total_cost)

        except Exception as e:
            context['error'] = str(e)

        return render(request, 'eventinfo/booking_confirmation.html', context)

    else:
        return HttpResponseRedirect(reverse('eventinfo:event_list'))
