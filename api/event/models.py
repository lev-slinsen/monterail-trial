from django.db import models

from api.event.utilities import CreatedUpdated


class Event(CreatedUpdated):
    CATEGORY_CHOICES = [
        ('even', 'Even'),
        ('avoid_one', 'Avoid one'),
        ('all_together', 'All together')
    ]
    title = models.CharField(max_length=255, unique=True, verbose_name='Event title')
    datetime_start = models.DateTimeField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title


class EventRow(models.Model):
    related_event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_rows')
    # TODO: Prevent purchased tickets deletion
    title = models.CharField(max_length=255)
    number_of_seats = models.SmallIntegerField()
    ticket_price = models.IntegerField()

    def __str__(self):
        return f'row {self.title} | {self.related_event.title}'

    def save(self, *args, **kwargs):
        # Prevents changing number of seats and adding rows with same title
        if (self.title,) in EventRow.objects.filter(related_event=self.related_event).values_list('title'):
            return
            # TODO: Throw an exception
        super(self.__class__, self).save(*args, **kwargs)
