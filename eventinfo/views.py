from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from eventinfo.models import Event, Event_types, Time_Slots, Tickets
from eventinfo.forms import EventSearchForm


def event_list(request):
    search_form = EventSearchForm(request.GET)
    events = Event.objects.all()
    if search_form.is_valid():
        events = events.filter(event_title__contains=search_form.cleaned_data['q'])

    types = Event_types.objects.all()
    context = {
        'search_form': search_form,
        'events': events,
        'types': types,
    }

    return render(request, 'eventinfo/events.html', context)


def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    guests = event.event_guests.all()
    time_slots = Time_Slots.objects.filter(event_id=event_id).order_by('event_start_date')
    tickets = Tickets.objects.filter(ticket_time_slot__event_id=event_id)

    context = {
        'guests': guests,
        'event': event,
        'time_slots': time_slots,
        'tickets': tickets,
    }

    return render(request, 'eventinfo/event.html', context)


def event_booking(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    guests = event.event_guests.all()

    context = {
        'guests': guests,
        'event': event,
    }

    return render(request, 'eventinfo/event_booking.html', context)


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
                'error': 'کاربری یا این مشخصات یافت نشد.',
            }
            return render(request, 'eventinfo/events.html/', context)

    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('eventinfo:event_list'))
        else:
            context = {}

    return render(request, 'eventinfo/events.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('eventinfo:event_list'))


@login_required
def account_profile(request):
    profile = request.user.profile
    context = {
        'profile': profile
    }

    return render(request, 'eventinfo/account/profile.html', context)
