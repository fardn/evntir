from django.contrib import admin

from eventinfo.models import Cities, Event_types, Event_organizers, Event_venues, Event, Guest, Profile, Time_Slots, \
    Tickets

admin.site.register(Cities)
admin.site.register(Event_types)
admin.site.register(Event_organizers)
admin.site.register(Event_venues)
admin.site.register(Event)
admin.site.register(Guest)
admin.site.register(Profile)
admin.site.register(Time_Slots)
admin.site.register(Tickets)



