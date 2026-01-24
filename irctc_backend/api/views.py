from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer
from django.db import transaction
from .models import Train, SeatInventory, Booking


# -----------------------------
# USER REGISTRATION
# -----------------------------

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


# -----------------------------
# AUTH TEST ENDPOINT
# -----------------------------

class ProtectedTestView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "message": "You are authenticated!",
            "user": request.user.username
        })


# -----------------------------
# BOOK TICKET (CONFIRM / WAITLIST)
# -----------------------------

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

                # ✅ CASE 1: Seats Available → CONFIRMED
                if seat.available_seats >= seats_required:

                    seat.available_seats -= seats_required
                    seat.save()

                    booking = Booking.objects.create(
                        user=request.user,
                        train_id=train_id,
                        travel_date=travel_date,
                        seats_booked=seats_required,
                        status='CONFIRMED'
                    )

                    return Response({
                        "message": "Ticket CONFIRMED",
                        "booking_id": booking.id,
                        "status": "CONFIRMED"
                    })


                # ✅ CASE 2: Seats Full → WAITLISTED
                else:

                    booking = Booking.objects.create(
                        user=request.user,
                        train_id=train_id,
                        travel_date=travel_date,
                        seats_booked=seats_required,
                        status='WAITLISTED'
                    )

                    return Response({
                        "message": "Ticket WAITLISTED",
                        "booking_id": booking.id,
                        "status": "WAITLISTED"
                    })

        except SeatInventory.DoesNotExist:

            return Response(
                {"error": "Seat inventory not found"},
                status=status.HTTP_404_NOT_FOUND
            )


# -----------------------------
# CANCEL BOOKING + AUTO UPGRADE WAITLIST
# -----------------------------

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
                        status=status.HTTP_400_BAD_REQUEST
                    )

                seat = SeatInventory.objects.select_for_update().get(
                    train=booking.train,
                    travel_date=booking.travel_date
                )

                # Restore seats
                seat.available_seats += booking.seats_booked
                seat.save()

                # Cancel booking
                booking.status = "CANCELLED"
                booking.save()

                # ✅ AUTO CONFIRM WAITLIST
                waitlist_booking = Booking.objects.filter(
                    train=booking.train,
                    travel_date=booking.travel_date,
                    status='WAITLISTED'
                ).order_by('booking_time').first()

                if waitlist_booking:

                    waitlist_booking.status = 'CONFIRMED'
                    waitlist_booking.save()

                    seat.available_seats -= waitlist_booking.seats_booked
                    seat.save()

                return Response({
                    "message": "Booking cancelled successfully"
                })

        except Booking.DoesNotExist:

            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )


# -----------------------------
# BOOKING HISTORY
# -----------------------------

class BookingHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        bookings = Booking.objects.filter(
            user=request.user
        ).order_by('-booking_time')

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
