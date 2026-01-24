from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer
from django.db import transaction
from .models import Train, SeatInventory, Booking


class RegisterView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProtectedTestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "You are authenticated!",
            "user": request.user.username
        })

class BookTicketView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        train_id = request.data.get('train_id')
        travel_date = request.data.get('travel_date')
        seats_required = int(request.data.get('seats'))

        try:
            with transaction.atomic():

                seat = SeatInventory.objects.select_for_update().get(
                    train_id=train_id,
                    travel_date=travel_date
                )

                if seat.available_seats < seats_required:
                    return Response(
                        {"error": "Not enough seats available"},
                        status=400
                    )

                # Reduce seats
                seat.available_seats -= seats_required
                seat.save()

                # Create booking
                booking = Booking.objects.create(
                    user=request.user,
                    train_id=train_id,
                    travel_date=travel_date,
                    seats_booked=seats_required,
                    status='CONFIRMED'
                )

                return Response({
                    "message": "Ticket booked successfully",
                    "booking_id": booking.id
                })

        except SeatInventory.DoesNotExist:
            return Response(
                {"error": "Seat inventory not found"},
                status=404
            )

class CancelBookingView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        booking_id = request.data.get("booking_id")

        try:
            with transaction.atomic():

                booking = Booking.objects.select_for_update().get(
                    id=booking_id,
                    user=request.user
                )

                if booking.status == "CANCELLED":
                    return Response(
                        {"error": "Booking already cancelled"},
                        status=400
                    )

                seat = SeatInventory.objects.select_for_update().get(
                    train=booking.train,
                    travel_date=booking.travel_date
                )

                # Restore seats
                seat.available_seats += booking.seats_booked
                seat.save()

                # Update booking status
                booking.status = "CANCELLED"
                booking.save()

                return Response({
                    "message": "Booking cancelled successfully"
                })

        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=404
            )

class BookingHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')

        data = []

        for booking in bookings:
            data.append({
                "booking_id": booking.id,
                "train": booking.train.name,
                "travel_date": booking.travel_date,
                "seats": booking.seats_booked,
                "status": booking.status,
                "time": booking.booking_time
            })

        return Response(data)

