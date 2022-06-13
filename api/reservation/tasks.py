from celery import shared_task


@shared_task(name="unreserve_tickets")
def unreserve_tickets(reservation_id):
    from api.reservation.models import Reservation
    reservation = Reservation.objects.get(id=reservation_id)
    if reservation.status == 'reserved':
        reservation.delete()
