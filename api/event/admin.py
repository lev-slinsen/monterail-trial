from django.contrib import admin

from api.event.models import Event
from api.ticket.models import Ticket


class TicketInline(admin.TabularInline):
    # TODO: add pagination
    model = Ticket
    fields = ('id', 'row', 'seat', 'price', 'reservation')
    readonly_fields = ('id', 'reservation')
    ordering = ("id",)
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'datetime_start', 'category')
    fields = ('id', 'title', 'datetime_start', 'category', 'created_at', 'updated_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_filter = ('category',)
    inlines = (TicketInline,)
