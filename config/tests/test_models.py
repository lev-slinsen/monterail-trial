from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from api.event.models import Event, EventRow
from api.reservation.models import Reservation
from api.ticket.models import Ticket

User = get_user_model()
now = timezone.now()
tomorrow = now + timedelta(days=1)


class TestModels(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user_1')
        self.event = Event.objects.create(title='event', datetime_start=tomorrow)
        self.event_row = EventRow.objects.create(related_event=self.event, title='A', number_of_seats=3, ticket_price=1)
        self.reservation = Reservation.objects.create(user=self.user)

    def test_event(self):
        self.assertEqual(str(self.event), 'event')

    def test_event_row(self):
        self.assertEqual(self.event_row.title, 'A')

    def test_event_row_immutability(self):
        self.event_row_new = EventRow.objects.create(related_event=self.event, title='A', number_of_seats=5, ticket_price=2)

        self.event_row.refresh_from_db()
        self.assertEqual(self.event.event_rows.all().first().number_of_seats, self.event_row.number_of_seats)

    def test_ticket(self):
        tickets = Ticket.objects.filter(event_row=self.event_row)

        self.assertEqual(len(Ticket.objects.filter(event_row=self.event_row)), self.event_row.number_of_seats)
        self.assertEqual(tickets.first().status, None)
        self.assertEqual(tickets.first().price, self.event_row.ticket_price)

    def test_reservation(self):
        tickets = Ticket.objects.filter(event_row=self.event_row)

        self.assertEqual(tickets.first().price, self.event_row.ticket_price)
