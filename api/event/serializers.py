from rest_framework import serializers

from api.event.models import Event


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['id', 'title', 'datetime_start', 'category']
