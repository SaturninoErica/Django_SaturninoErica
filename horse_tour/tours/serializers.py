from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import Booking, Review, Tour, TourCategory, TouristProfile


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TouristProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristProfile
        fields = ["id", "user", "phone"]


class TourCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TourCategory
        fields = ["id", "name", "description"]


class TourSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=TourCategory.objects.all(),
    )

    class Meta:
        model = Tour
        fields = ["id", "title", "description", "price", "categories"]
        read_only_fields = ["id"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "user", "tour", "scheduled_at", "status"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        user = attrs.get("user", getattr(self.instance, "user", None))
        scheduled_at = attrs.get(
            "scheduled_at",
            getattr(self.instance, "scheduled_at", None),
        )
        if user is not None and scheduled_at is not None:
            existing = Booking.objects.filter(
                user=user,
                scheduled_at=scheduled_at,
            )
            if self.instance is not None:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError(
                    {
                        "scheduled_at": (
                            "Пользователь уже записан на тур в это время."
                        )
                    }
                )
        return attrs

    def create(self, validated_data):
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as error:
            raise serializers.ValidationError(
                {"scheduled_at": "Это время уже занято для пользователя."}
            ) from error


class ReviewSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ["id", "user", "tour", "rating", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        user = attrs.get("user", getattr(self.instance, "user", None))
        tour = attrs.get("tour", getattr(self.instance, "tour", None))
        if user is not None and tour is not None:
            attended = Booking.objects.filter(
                user=user,
                tour=tour,
                status=Booking.Status.COMPLETED,
            ).exists()
            if not attended:
                raise serializers.ValidationError(
                    "Оставить отзыв можно только о завершенном туре."
                )
        return attrs
