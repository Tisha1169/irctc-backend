from django.urls import path
from .views import RegisterView, ProtectedTestView, BookTicketView, CancelBookingView, BookingHistoryView, AdminStatsView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('protected/', ProtectedTestView.as_view(), name='protected'),
    path('book/', BookTicketView.as_view(), name='book'),
    path('cancel/', CancelBookingView.as_view(), name='cancel'),
    path('history/', BookingHistoryView.as_view(), name='history'),
    path('admin/stats/', AdminStatsView.as_view()),



]