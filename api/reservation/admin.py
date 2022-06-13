from django.contrib import admin

from api.reservation.models import Reservation
from api.ticket.models import Ticket


class TicketInline(admin.TabularInline):
    # TODO: add pagination
    model = Ticket
    fields = ('id', 'event_row', 'seat', 'status')
    readonly_fields = fields
    ordering = ("id",)
    extra = 0


@admin.register(Reservation)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id',)
    fields = ('id', 'created_at', 'updated_at')
    readonly_fields = fields
    inlines = [TicketInline]
