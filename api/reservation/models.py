from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.event.utilities import CreatedUpdated
from api.reservation.tasks import unreserve_tickets

User = get_user_model()


class Reservation(CreatedUpdated):
    STATUS_CHOICES = [
        ('reserved', 'Reserved'),
        ('purchased', 'Purchased'),
    ]
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def total_price(self):
        return sum(ticket.price for ticket in self.tickets.all())

    @classmethod
    def expiration_timer(cls):
        # Deletes the object if it hasn't been purchased, in seconds
        return 900


@receiver(post_save, sender=Reservation)
def set_expiration_timer(sender, instance, created, **kwargs):
    if created:
        unreserve_tickets.apply_async((instance.id,), countdown=sender.expiration_timer())
