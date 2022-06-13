from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.event.utilities import CustomPageNumberPagination
from api.reservation.models import Reservation
from api.reservation.serializers import ReservationSerializer, PaymentSerializer


class ReservationCreateView(generics.CreateAPIView):
    """
    {'tickets': [45, 80],}
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationSerializer

    def post(self, request, *args, **kwargs):
        # Capturing user from request
        request.data['user'] = request.user.id
        response = self.create(request, *args, **kwargs)
        return response


class ReservationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        qs = Reservation.objects \
            .filter(user__id=self.request.user.id) \
            .annotate(tickets_count=Count('tickets')) \
            .exclude(tickets_count=0) \
            .order_by('-created_at')
        return qs


class ReservationPayView(APIView):
    # TODO: Add body field to Swagger
    """
    {
        "reservation": 1,
        "amount": 123,
        "token": "token",
        "currency": "GBP"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Capturing user from request
        request.data['user'] = request.user.id
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
