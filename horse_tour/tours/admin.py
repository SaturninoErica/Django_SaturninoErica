from django.contrib import admin

from .models import Booking, Review, Tour, TourCategory, TouristProfile


admin.site.register(TouristProfile)
admin.site.register(TourCategory)
admin.site.register(Tour)
admin.site.register(Booking)
admin.site.register(Review)
