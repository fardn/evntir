from django.shortcuts import render, get_object_or_404

from eventinfo.models import Event, Event_types
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

    context = {
        'guests': guests,
        'event': event,
    }

    return render(request, 'eventinfo/event.html', context)
