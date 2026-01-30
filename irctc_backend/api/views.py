from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer
from django.db import transaction

from .models import Train, Booking, SeatInventory, Station
from .mongo import booking_logs_collection, search_logs_collection
from datetime import datetime

class TrainSearchView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        source_code = request.GET.get("source")
        dest_code = request.GET.get("destination")

        if not source_code or not dest_code:
            return Response(
                {"error": "source and destination required"},
                status=400
            )

        try:
            source = Station.objects.get(code=source_code)
            destination = Station.objects.get(code=dest_code)

            trains = Train.objects.filter(
                source=source,
                destination=destination
            )

            result = []

            for train in trains:
                result.append({
                    "id": train.id,
                    "train_number": train.train_number,
                    "name": train.name,
                    "source": source.name,
                    "destination": destination.name
                })

            # MongoDB logging
            search_logs_collection.insert_one({
                "user": request.user.username,
                "source": source_code,
                "destination": dest_code,
                "time": datetime.now()
            })

            return Response(result)

        except Station.DoesNotExist:
            return Response(
                {"error": "Invalid station code"},
                status=404
            )


# -----------------------------
# REGISTER
# -----------------------------

class RegisterView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=201)

        return Response(serializer.errors, status=400)


# -----------------------------
# AUTH TEST
# -----------------------------

class ProtectedTestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "message": "Authenticated",
            "user": request.user.username
        })


# -----------------------------
# BOOK TICKET
# -----------------------------

class BookTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        train_id = request.data.get('train_id')
        travel_date = request.data.get('travel_date')
        seats = request.data.get('seats')

        if not train_id or not travel_date or not seats:
            return Response({"error": "Missing fields"}, status=400)

        seats_required = int(seats)

        try:
            with transaction.atomic():

                train = Train.objects.get(id=train_id)

                # ✅ AUTO CREATE SEAT INVENTORY
                seat, created = SeatInventory.objects.select_for_update().get_or_create(
                    train=train,
                    travel_date=travel_date,
                    defaults={
                        "total_seats": 100,
                        "available_seats": 100
                    }
                )

                # CONFIRMED
                if seat.available_seats >= seats_required:

                    seat.available_seats -= seats_required
                    seat.save()

                    booking = Booking.objects.create(
                        user=request.user,
                        train=train,
                        travel_date=travel_date,
                        seats_booked=seats_required,
                        status='CONFIRMED'
                    )

                    self.mongo_log(request.user.username, "BOOK", booking.id, "CONFIRMED")

                    return Response({
                        "message": "Ticket CONFIRMED",
                        "booking_id": booking.id
                    })

                # WAITLIST
                booking = Booking.objects.create(
                    user=request.user,
                    train=train,
                    travel_date=travel_date,
                    seats_booked=seats_required,
                    status='WAITLIST'
                )

                self.mongo_log(request.user.username, "BOOK", booking.id, "WAITLIST")

                return Response({
                    "message": "Ticket WAITLISTED",
                    "booking_id": booking.id
                })

        except Train.DoesNotExist:
            return Response({"error": "Train not found"}, status=404)


    def mongo_log(self, user, action, booking_id, status):

        try:
            booking_logs_collection.insert_one({
                "user": user,
                "action": action,
                "booking_id": booking_id,
                "status": status
            })
        except:
            pass


# -----------------------------
# CANCEL BOOKING
# -----------------------------

class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        booking_id = request.data.get("booking_id")

        if not booking_id:
            return Response({"error": "booking_id required"}, status=400)

        try:
            with transaction.atomic():

                booking = Booking.objects.select_for_update().get(
                    id=booking_id,
                    user=request.user
                )

                if booking.status == "CANCELLED":
                    return Response({"error": "Already cancelled"}, status=400)

                seat = SeatInventory.objects.select_for_update().get(
                    train=booking.train,
                    travel_date=booking.travel_date
                )

                # restore seat
                seat.available_seats += booking.seats_booked
                seat.save()

                booking.status = "CANCELLED"
                booking.save()

                # AUTO PROMOTE WAITLIST
                waitlist = Booking.objects.filter(
                    train=booking.train,
                    travel_date=booking.travel_date,
                    status='WAITLIST'
                ).order_by('booking_time').first()

                if waitlist and seat.available_seats >= waitlist.seats_booked:

                    waitlist.status = 'CONFIRMED'
                    waitlist.save()

                    seat.available_seats -= waitlist.seats_booked
                    seat.save()

                return Response({"message": "Booking cancelled"})

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)


# -----------------------------
# HISTORY
# -----------------------------

class BookingHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        bookings = Booking.objects.filter(user=request.user)

        data = []

        for b in bookings:
            data.append({
                "booking_id": b.id,
                "train": b.train.name,
                "date": b.travel_date,
                "seats": b.seats_booked,
                "status": b.status
            })

        return Response(data)


# -----------------------------
# ADMIN STATS
# -----------------------------

class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_staff:
            return Response({"error": "Admin only"}, status=403)

        return Response({
            "total_bookings": Booking.objects.count(),
            "confirmed": Booking.objects.filter(status='CONFIRMED').count(),
            "waitlisted": Booking.objects.filter(status='WAITLIST').count(),
            "cancelled": Booking.objects.filter(status='CANCELLED').count(),
            "total_trains": Train.objects.count()
        })
