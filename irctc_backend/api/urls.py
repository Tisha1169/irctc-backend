from django.urls import path
from .views import (
    RegisterView,
    ProtectedTestView,
    BookTicketView,
    CancelBookingView,
    BookingHistoryView,
    AdminStatsView,
    TrainSearchView
)

from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [

    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('protected/', ProtectedTestView.as_view(), name='protected'),

    # Booking
    path('book/', BookTicketView.as_view(), name='book'),
    path('cancel/', CancelBookingView.as_view(), name='cancel'),
    path('history/', BookingHistoryView.as_view(), name='history'),

    # Admin
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('trains/search/', TrainSearchView.as_view()),


]
