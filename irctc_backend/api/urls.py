from django.urls import path
from .views import RegisterView, ProtectedTestView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('protected/', ProtectedTestView.as_view(), name='protected'),
]
