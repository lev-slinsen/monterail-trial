from django.contrib import admin

from api.ticket.models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    # TODO: Add search by event
    list_display = ('id', 'event', 'row', 'seat', 'price')
    fields = ('id', 'event', 'seat', 'row', 'price', 'reservation')
    readonly_fields = ('id', 'reservation')
    list_filter = ('event', 'reservation__status')

    def has_add_permission(self, request, obj=None):
        return False
