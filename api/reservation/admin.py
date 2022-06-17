from django.contrib import admin

from api.reservation.models import Reservation


@admin.register(Reservation)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id',)
    fields = ('id', 'created_at', 'updated_at')
    readonly_fields = fields
