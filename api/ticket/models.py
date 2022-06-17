from django.db import models

from api.event.models import Event
from api.reservation.models import Reservation


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    seat = models.SmallIntegerField()
    row = models.CharField(max_length=255, null=True, blank=True, default=None)
    price = models.PositiveSmallIntegerField()
    reservation = models.ForeignKey(Reservation, default=None, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='tickets')

    @property
    def status(self):
        return self.reservation.status if self.reservation else None

    def __str__(self):
        return f'seat {self.seat} | {self.row}'

    class Meta:
        unique_together = ['seat', 'row', 'event']


def create_row(event, seats, price, row=None):
    try:
        tickets = [Ticket(event=event, seat=s+1, row=row, price=price) for s in range(seats)]
        Ticket.objects.bulk_create(tickets)
        return True
    except Exception as ex:
        return ex
