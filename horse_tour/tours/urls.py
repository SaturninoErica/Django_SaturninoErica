from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BookingViewSet,
    ReviewViewSet,
    TourCategoryViewSet,
    TourViewSet,
    TouristProfileViewSet,
    UserRegistrationView,
)


router = DefaultRouter()
router.register("profiles", TouristProfileViewSet)
router.register("categories", TourCategoryViewSet)
router.register("tours", TourViewSet)
router.register("bookings", BookingViewSet)
router.register("reviews", ReviewViewSet)

urlpatterns = [
    path("users/", UserRegistrationView.as_view(), name="user-registration"),
    path("", include(router.urls)),
]
