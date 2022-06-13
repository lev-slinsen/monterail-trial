from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.event.models import EventRow
from api.reservation.models import Reservation


class Ticket(models.Model):
    event_row = models.ForeignKey(EventRow, on_delete=models.CASCADE, related_name='tickets')
    seat = models.SmallIntegerField()
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='tickets')

    @property
    def status(self):
        return self.reservation.status if self.reservation else None

    @property
    def price(self):
        return self.event_row.ticket_price

    def __str__(self):
        return f'seat {self.seat} | {self.event_row}'


@receiver(post_save, sender=EventRow)
def create_tickets(sender, instance, **kwargs):
    tickets = [Ticket(event_row=instance, seat=s+1) for s in range(instance.number_of_seats)]
    Ticket.objects.bulk_create(tickets)
