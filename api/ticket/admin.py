from django.contrib import admin

from api.ticket.models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    # TODO: Add search by event
    list_display = ('id', 'seat', 'event_row', 'status')
    fields = ('id', 'seat', 'event_row', 'status', 'reservation', 'price')
    readonly_fields = fields
    list_filter = ('event_row__related_event',)

    def has_add_permission(self, request, obj=None):
        return False
