from django.contrib import admin
from .models import Station, Train, TrainRoute, SeatInventory, Booking


# -------------------------
# STATION ADMIN
# -------------------------

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')


# -------------------------
# TRAIN ADMIN
# -------------------------

@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ('id', 'train_number', 'name', 'source', 'destination')
    search_fields = ('train_number', 'name')
    list_filter = ('source', 'destination')


# -------------------------
# TRAIN ROUTE ADMIN
# -------------------------

@admin.register(TrainRoute)
class TrainRouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'train', 'station', 'stop_number')
    list_filter = ('train',)
    ordering = ('train', 'stop_number')


# -------------------------
# SEAT INVENTORY ADMIN
# -------------------------

@admin.register(SeatInventory)
class SeatInventoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'train',
        'travel_date',
        'total_seats',
        'available_seats'
    )
    list_filter = ('travel_date', 'train')
    search_fields = ('train__train_number',)


# -------------------------
# BOOKING ADMIN
# -------------------------

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'train',
        'travel_date',
        'seats_booked',
        'status',
        'booking_time'
    )

    list_filter = ('status', 'travel_date')
    search_fields = ('user__username', 'train__train_number')
    ordering = ('-booking_time',)
