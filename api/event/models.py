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
