from django.db import models
from django.contrib.auth.models import User


class Station(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"
    

class Train(models.Model):
    train_number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    source = models.ForeignKey(
        Station,
        related_name='source_trains',
        on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Station,
        related_name='destination_trains',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.train_number} - {self.name}"
   
class TrainRoute(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    stop_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('train', 'station')
        ordering = ['stop_number']

    def __str__(self):
        return f"{self.train} - Stop {self.stop_number} at {self.station}"

class SeatInventory(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    travel_date = models.DateField()
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()

    class Meta:
        unique_together = ('train', 'travel_date')

    def __str__(self):
        return f"{self.train} | {self.travel_date} | Available: {self.available_seats}"


class Booking(models.Model):

    STATUS_CHOICES = (
    ('CONFIRMED', 'Confirmed'),
    ('WAITLIST', 'Waitlist'),
    ('CANCELLED', 'Cancelled'),
)


    user = models.ForeignKey(User, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    travel_date = models.DateField()
    seats_booked = models.IntegerField(default=1)
    booking_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.user.username} | {self.train} | {self.status}"
