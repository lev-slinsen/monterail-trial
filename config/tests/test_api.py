from copy import copy
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from api.event.models import Event, EventRow
from api.reservation.models import Reservation

User = get_user_model()
now = timezone.now()
tomorrow = now + timedelta(days=1)


class ApiTest(APITestCase):

    def setUp(self):
        # Users
        #
        self.user = User.objects.create(username='user_1')

        # Events
        #
        self.event =                Event.objects.create(title='event', datetime_start=tomorrow)
        self.event_past =           Event.objects.create(title='event_past', datetime_start=now - timedelta(days=1))
        self.event_even =           Event.objects.create(title='event_even', datetime_start=tomorrow, category='even')
        self.event_avoid_one =      Event.objects.create(title='event_avoid_one', datetime_start=tomorrow, category='avoid_one')
        self.event_all_together =   Event.objects.create(title='event_all_together', datetime_start=tomorrow, category='all_together')

        # Rows and tickets
        #
        self.event_row =                        EventRow.objects.create(related_event=self.event, title='A', number_of_seats=3, ticket_price=1)
        self.tickets_event_row =                self.event_row.tickets.all()

        self.event_even_row =                   EventRow.objects.create(related_event=self.event_even, title='A', number_of_seats=3, ticket_price=1)
        self.tickets_event_even_row =           self.event_even_row.tickets.all()

        self.event_avoid_one_row_a =            EventRow.objects.create(related_event=self.event_avoid_one, title='A', number_of_seats=3, ticket_price=1)
        self.tickets_event_avoid_one_row_a =    self.event_avoid_one_row_a.tickets.all()
        self.event_avoid_one_row_b =            EventRow.objects.create(related_event=self.event_avoid_one, title='B', number_of_seats=3, ticket_price=1)
        self.tickets_event_avoid_one_row_b =    self.event_avoid_one_row_b.tickets.all()

        self.event_all_together_row_a =         EventRow.objects.create(related_event=self.event_all_together, title='A', number_of_seats=3, ticket_price=1)
        self.tickets_event_all_together_row_a = self.event_all_together_row_a.tickets.all()
        self.event_all_together_row_b =         EventRow.objects.create(related_event=self.event_all_together, title='B', number_of_seats=3, ticket_price=1)
        self.tickets_event_all_together_row_b = self.event_all_together_row_b.tickets.all()


class TestEvent(ApiTest):

    def test_event_errors(self):
        res = self.client.get(reverse('event_list'))
        self.assertEqual(res.status_code, 403)

    def test_event_list(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse('event_list'))

        self.assertEqual(res.data['count'], len(Event.objects.filter(datetime_start__gte=now)))
        assert 'id' in res.data['results'][0]
        assert 'title' in res.data['results'][0]
        assert 'datetime_start' in res.data['results'][0]
        assert 'category' in res.data['results'][0]


class TestReservation(ApiTest):

    def test_reservation_errors(self):
        res = self.client.post(reverse('reservation_create'))
        self.assertEqual(res.status_code, 403)

        res = self.client.get(reverse('my_reservations'))
        self.assertEqual(res.status_code, 403)

        res = self.client.post(reverse('reservation_pay'))
        self.assertEqual(res.status_code, 403)

        self.client.force_login(self.user)

        data = {"tickets": ''}
        res = self.client.post(reverse('reservation_create'), data, format='json')
        self.assertEqual(res.status_code, 400)

    def test_reservation_and_payment(self):
        self.client.force_login(self.user)

        # Create new reservation
        #
        data = {"tickets": [100500]}
        res = self.client.post(reverse('reservation_create'), data, format='json')

        self.assertEqual(res.status_code, 400)

        data = {"tickets": list(self.tickets_event_row.values_list('id', flat=True))}
        res = self.client.post(reverse('reservation_create'), data, format='json')

        self.assertEqual(res.data['tickets'], list(self.tickets_event_row.values_list('id', flat=True)))
        self.assertEqual(res.data['user'], self.user.id)
        self.assertEqual(res.data['status'], 'reserved')

        reservation = Reservation.objects.all().first()

        # Test my reservations list
        #
        res = self.client.get(reverse('my_reservations'))
        self.assertEqual(res.data['count'], len(Reservation.objects.filter(user=self.user)))

        # Test payment errors
        #
        valid_data = {
            "reservation": reservation.id,
            "amount": reservation.total_price,
            "token": "token",
            "currency": "GBP",
        }

        data = copy(valid_data)
        data['reservation'] = data['reservation'] + 1000
        res = self.client.post(reverse('reservation_pay'), data, format='json')
        self.assertEqual(res.status_code, 400)

        data = copy(valid_data)
        data['amount'] = data['amount'] + 1000
        res = self.client.post(reverse('reservation_pay'), data, format='json')
        self.assertEqual(res.status_code, 400)

        data = copy(valid_data)
        data['token'] = 'card_error'
        res = self.client.post(reverse('reservation_pay'), data, format='json')
        self.assertEqual(res.status_code, 400)

        data = copy(valid_data)
        data['token'] = 'payment_error'
        res = self.client.post(reverse('reservation_pay'), data, format='json')
        self.assertEqual(res.status_code, 400)

        data = copy(valid_data)
        data['currency'] = 'USD'
        res = self.client.post(reverse('reservation_pay'), data, format='json')
        self.assertEqual(res.status_code, 400)

        # Test payment
        #
        res = self.client.post(reverse('reservation_pay'), valid_data, format='json')
        self.assertEqual(res.data['reservation'], reservation.id)
        self.assertEqual(res.data['amount'], reservation.total_price)
        self.assertEqual(res.data['token'], 'token')
        self.assertEqual(res.data['currency'], 'GBP')
        self.assertEqual(res.data['user'], self.user.id)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'purchased')

    def test_reservation_even(self):
        self.client.force_login(self.user)
        ticket_ids = list(self.tickets_event_even_row.values_list('id', flat=True))

        if len(ticket_ids) > 1 and (len(ticket_ids) % 2) == 0:
            ticket_ids.pop()
        data = {"tickets": ticket_ids}
        res = self.client.post(reverse('reservation_create'), data, format='json')
        self.assertEqual(res.status_code, 400)

        if len(ticket_ids) > 1 and (len(ticket_ids) % 2) != 0:
            ticket_ids.pop()
        data = {"tickets": ticket_ids}
        res = self.client.post(reverse('reservation_create'), data, format='json')
        self.assertEqual(res.status_code, 201)

    def test_reservation_avoid_one(self):
        self.client.force_login(self.user)
        ticket_ids_row_a = list(self.tickets_event_avoid_one_row_a.values_list('id', flat=True))
        ticket_ids_row_b = list(self.tickets_event_avoid_one_row_b.values_list('id', flat=True))

        # _ vacant
        # * in operation
        # = reserved

        # [ * _ _ ] Error
        # [ * * * ]
        data = {"tickets": ticket_ids_row_a[0:2] + ticket_ids_row_b}
        res = self.client.post(reverse('reservation_create'), data, format='json')
        self.assertEqual(res.status_code, 400)

        # [ * _ _ ]
        # [ * _ _ ]
        data = {"tickets": [ticket_ids_row_a[0]] + [ticket_ids_row_b[0]]}
        res = self.client.post(reverse('reservation_create'), data, format='json')
        self.assertEqual(res.status_code, 201)

        # [ = * _ ] Error
        # [ = _ _ ]
        data = {"tickets": ticket_ids_row_a[1]}
        res = self.client.post(reverse('reservation_create'), data, format='json')
        self.assertEqual(res.status_code, 400)

        # [ * * * ] Error
        # [ = _ _ ]
        data = {"tickets": ticket_ids_row_a}
        res = self.client.post(reverse('reservation_create'), data, format='json')
        self.assertEqual(res.status_code, 400)

        # [ = * * ]
        # [ = * * ]
        data = {"tickets": ticket_ids_row_a[1:3] + ticket_ids_row_b[1:3]}
        res = self.client.post(reverse('reservation_create'), data, format='json')
        self.assertEqual(res.status_code, 201)

    def test_reservation_create_all_together(self):
        self.client.force_login(self.user)
        ticket_ids_row_a = list(self.tickets_event_all_together_row_a.values_list('id', flat=True))
        ticket_ids_row_b = list(self.tickets_event_all_together_row_b.values_list('id', flat=True))

        # _ vacant
        # * in operation
        # = reserved

        # [ * _ * ] Error
        # [ * * * ]
        data = {"tickets": [ticket_ids_row_a[0], ticket_ids_row_a[-1]] + ticket_ids_row_b}
        res = self.client.post(reverse('reservation_create'), data, format='json')
        self.assertEqual(res.status_code, 400)

        # [ * * _ ]
        # [ _ _ * ]
        data = {"tickets": ticket_ids_row_a[0:2] + [ticket_ids_row_b[-1]]}
        res = self.client.post(reverse('reservation_create'), data, format='json')
        self.assertEqual(res.status_code, 201)


class TestTicket(ApiTest):

    def test_ticket_list_errors(self):
        res = self.client.get(reverse('ticket_list', kwargs={'event_id': 1}))
        self.assertEqual(res.status_code, 403)

    def test_ticket_list(self):
        self.client.force_login(self.user)

        res = self.client.get(reverse('ticket_list', kwargs={'event_id': self.event.id}))
        self.assertEqual(res.data['count'], len(self.event_row.tickets.all()))

        res = self.client.get(reverse('ticket_list', kwargs={'event_id': self.event.id + 1000}))
        self.assertEqual(res.data['count'], 0)
