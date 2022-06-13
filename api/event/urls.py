from django.urls import path

from api.event.views import EventListView


urlpatterns = [
    path('event/list/', EventListView.as_view(), name='event_list'),
]
