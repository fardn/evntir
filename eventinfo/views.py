from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from eventinfo.models import Event, Event_types, Time_Slots, Tickets, Time_slot_status
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
def event_booking(request, event_id):

    if request.method == 'POST':
        ticket_list = request.POST.items()
        #ticket_id = ticket_list['ticket-id']
        book_ticket = get_object_or_404(Tickets, pk=10)
        #book_seats = int(request.POST['book_seats'])
        event = get_object_or_404(Event, pk=event_id)
        guests = event.event_guests.all()
        #book_total_cost = int(book_ticket.ticket_price)*book_seats
        ticket_status = book_ticket.get_status
        context = {
            #'ticket_id':ticket_id,
            #'ticket_key': ticket_key,
            #'ticket_value': ticket_value,
            'ticket_list':ticket_list,
            'ticket_status': ticket_status,
            'book_ticket': book_ticket,
            #'book_seats': book_seats,
            #'book_total_cost': book_total_cost,
            'event': event,
            'guests': guests,
            'message': 'پروفایل با موفقیت ویرایش شد.',
            'error': True,
        }
        return render(request, 'eventinfo/event_booking.html', context)

    else:
        return HttpResponseRedirect(reverse('eventinfo:event_list'))


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
    event_type_list = events.values('event_type', 'event_type__type_title', 'event_type__type_icon').annotate(count=Count('event_type'))
    types = Event_types.objects.all()
    context = {
        'search_form': search_form,
        'event_type_list': event_type_list,
        'events': events,
        'types': types,
    }

    return render(request, 'eventinfo/index.html', context)

@login_required
def booking_confirmation(request):
    pass