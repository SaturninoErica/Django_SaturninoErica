from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView

from .models import Booking, Review, Tour, TourCategory, TouristProfile
from .serializers import (
    BookingSerializer,
    ReviewSerializer,
    TourCategorySerializer,
    TourSerializer,
    TouristProfileSerializer,
    UserRegistrationSerializer,
)


class UserRegistrationView(CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserRegistrationSerializer


class TouristProfileViewSet(viewsets.ModelViewSet):
    queryset = TouristProfile.objects.select_related("user").all()
    serializer_class = TouristProfileSerializer


class TourCategoryViewSet(viewsets.ModelViewSet):
    queryset = TourCategory.objects.all()
    serializer_class = TourCategorySerializer


class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.prefetch_related("categories").all()
    serializer_class = TourSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related("user", "tour").all()
    serializer_class = BookingSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("user", "tour").all()
    serializer_class = ReviewSerializer
