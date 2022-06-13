from django.contrib import admin

from api.event.models import Event, EventRow


class EventRowInline(admin.TabularInline):
    # TODO: add pagination
    model = EventRow
    fields = ('id', 'title', 'number_of_seats', 'ticket_price')
    readonly_fields = ('id',)
    ordering = ("id",)
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'datetime_start', 'category')
    fields = ('id', 'title', 'datetime_start', 'category', 'created_at', 'updated_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_filter = ('category',)
    inlines = (EventRowInline,)
