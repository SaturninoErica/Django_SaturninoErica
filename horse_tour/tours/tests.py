from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Booking, Review, Tour, TourCategory, TouristProfile


User = get_user_model()


class HorseTourApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="rider",
            password="secure-password-123",
            email="rider@example.com",
        )
        self.other_user = User.objects.create_user(
            username="another-rider",
            password="secure-password-456",
        )
        self.category = TourCategory.objects.create(
            name="Конный",
            description="Маршруты верхом",
        )
        self.second_category = TourCategory.objects.create(name="Пеший")
        self.tour = Tour.objects.create(
            title="Горный конный маршрут",
            description="Маршрут по горной долине",
            price="125.00",
        )
        self.tour.categories.add(self.category)
        self.scheduled_at = timezone.now() + timedelta(days=5)

    def test_api_documentation_endpoints_are_available(self):
        schema = self.client.get(reverse("schema"))
        docs = self.client.get(reverse("swagger-ui"))

        self.assertEqual(schema.status_code, 200)
        self.assertEqual(docs.status_code, 200)

    def test_user_registration_creates_hashed_password(self):
        response = self.client.post(
            reverse("user-registration"),
            {
                "username": "new-rider",
                "email": "new@example.com",
                "password": "long-password-123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        created_user = User.objects.get(username="new-rider")
        self.assertTrue(created_user.check_password("long-password-123"))
        self.assertNotIn("password", response.data)

    def test_user_registration_rejects_short_password(self):
        response = self.client.post(
            reverse("user-registration"),
            {"username": "new-rider", "password": "short"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username="new-rider").exists())

    def test_profile_create_read_update_and_delete(self):
        response = self.client.post(
            reverse("touristprofile-list"),
            {"user": self.user.pk, "phone": "+77001234567"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        profile_id = response.data["id"]
        self.assertEqual(
            self.client.get(
                reverse("touristprofile-detail", args=[profile_id])
            ).status_code,
            200,
        )
        update = self.client.put(
            reverse("touristprofile-detail", args=[profile_id]),
            {"user": self.user.pk, "phone": "+77007654321"},
            format="json",
        )
        self.assertEqual(update.status_code, 200)
        partial_update = self.client.patch(
            reverse("touristprofile-detail", args=[profile_id]),
            {"phone": "+77000000000"},
            format="json",
        )
        self.assertEqual(partial_update.status_code, 200)
        self.assertEqual(partial_update.data["phone"], "+77000000000")
        self.assertEqual(
            self.client.delete(
                reverse("touristprofile-detail", args=[profile_id])
            ).status_code,
            204,
        )
        self.assertFalse(TouristProfile.objects.filter(pk=profile_id).exists())

    def test_profile_one_to_one_rejects_second_profile(self):
        TouristProfile.objects.create(user=self.user, phone="111")

        response = self.client.post(
            reverse("touristprofile-list"),
            {"user": self.user.pk, "phone": "222"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TouristProfile.objects.filter(user=self.user).count(), 1)

    def test_category_create_read_update_and_delete(self):
        response = self.client.post(
            reverse("tourcategory-list"),
            {"name": "Мото", "description": "Поездки на мотоцикле"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        category_id = response.data["id"]
        self.assertEqual(
            self.client.get(
                reverse("tourcategory-detail", args=[category_id])
            ).status_code,
            200,
        )
        update = self.client.put(
            reverse("tourcategory-detail", args=[category_id]),
            {"name": "Мото-тур", "description": "Новый маршрут"},
            format="json",
        )
        self.assertEqual(update.status_code, 200)
        partial_update = self.client.patch(
            reverse("tourcategory-detail", args=[category_id]),
            {"description": "Обновленное описание"},
            format="json",
        )
        self.assertEqual(partial_update.status_code, 200)
        self.assertEqual(
            self.client.delete(
                reverse("tourcategory-detail", args=[category_id])
            ).status_code,
            204,
        )

    def test_tour_create_saves_many_to_many_categories_and_crud(self):
        response = self.client.post(
            reverse("tour-list"),
            {
                "title": "Пешая прогулка",
                "description": "Лесной маршрут",
                "price": "75.00",
                "categories": [self.category.pk, self.second_category.pk],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        tour_id = response.data["id"]
        self.assertCountEqual(
            response.data["categories"],
            [self.category.pk, self.second_category.pk],
        )
        self.assertEqual(
            self.client.get(reverse("tour-detail", args=[tour_id])).status_code,
            200,
        )
        update = self.client.put(
            reverse("tour-detail", args=[tour_id]),
            {
                "title": "Обновленный тур",
                "description": "Новое описание",
                "price": "90.00",
                "categories": [self.second_category.pk],
            },
            format="json",
        )
        self.assertEqual(update.status_code, 200)
        partial_update = self.client.patch(
            reverse("tour-detail", args=[tour_id]),
            {"price": "99.00"},
            format="json",
        )
        self.assertEqual(partial_update.status_code, 200)
        self.assertEqual(partial_update.data["price"], "99.00")
        self.assertEqual(
            self.client.delete(reverse("tour-detail", args=[tour_id])).status_code,
            204,
        )
        self.assertFalse(Tour.objects.filter(pk=tour_id).exists())

    def test_tour_requires_existing_categories(self):
        response = self.client.post(
            reverse("tour-list"),
            {
                "title": "Без категории",
                "description": "Описание",
                "price": "10.00",
                "categories": [99999],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_booking_create_read_update_and_delete(self):
        response = self.client.post(
            reverse("booking-list"),
            {
                "user": self.user.pk,
                "tour": self.tour.pk,
                "scheduled_at": self.scheduled_at.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        booking_id = response.data["id"]
        self.assertEqual(
            self.client.get(
                reverse("booking-detail", args=[booking_id])
            ).status_code,
            200,
        )
        update_time = self.scheduled_at + timedelta(days=1)
        update = self.client.put(
            reverse("booking-detail", args=[booking_id]),
            {
                "user": self.user.pk,
                "tour": self.tour.pk,
                "scheduled_at": update_time.isoformat(),
                "status": Booking.Status.CONFIRMED,
            },
            format="json",
        )
        self.assertEqual(update.status_code, 200)
        partial_update = self.client.patch(
            reverse("booking-detail", args=[booking_id]),
            {"status": Booking.Status.COMPLETED},
            format="json",
        )
        self.assertEqual(partial_update.status_code, 200)
        self.assertEqual(partial_update.data["status"], Booking.Status.COMPLETED)
        self.assertEqual(
            self.client.delete(
                reverse("booking-detail", args=[booking_id])
            ).status_code,
            204,
        )
        self.assertFalse(Booking.objects.filter(pk=booking_id).exists())

    def test_user_cannot_book_two_tours_at_the_same_time(self):
        Booking.objects.create(
            user=self.user,
            tour=self.tour,
            scheduled_at=self.scheduled_at,
        )
        other_tour = Tour.objects.create(
            title="Второй тур",
            description="Описание",
            price="50.00",
        )

        response = self.client.post(
            reverse("booking-list"),
            {
                "user": self.user.pk,
                "tour": other_tour.pk,
                "scheduled_at": self.scheduled_at.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Booking.objects.filter(user=self.user).count(), 1)

    def test_booking_unique_constraint_is_enforced_by_database(self):
        Booking.objects.create(
            user=self.user,
            tour=self.tour,
            scheduled_at=self.scheduled_at,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Booking.objects.create(
                user=self.user,
                tour=self.tour,
                scheduled_at=self.scheduled_at,
            )

    def test_review_create_read_update_and_delete(self):
        Booking.objects.create(
            user=self.user,
            tour=self.tour,
            scheduled_at=timezone.now() - timedelta(days=1),
            status=Booking.Status.COMPLETED,
        )
        response = self.client.post(
            reverse("review-list"),
            {
                "user": self.user.pk,
                "tour": self.tour.pk,
                "rating": 5,
                "comment": "Прекрасная поездка",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        review_id = response.data["id"]
        self.assertEqual(
            self.client.get(
                reverse("review-detail", args=[review_id])
            ).status_code,
            200,
        )
        update = self.client.put(
            reverse("review-detail", args=[review_id]),
            {
                "user": self.user.pk,
                "tour": self.tour.pk,
                "rating": 4,
                "comment": "Хорошая поездка",
            },
            format="json",
        )
        self.assertEqual(update.status_code, 200)
        partial_update = self.client.patch(
            reverse("review-detail", args=[review_id]),
            {"comment": "Очень хорошая поездка"},
            format="json",
        )
        self.assertEqual(partial_update.status_code, 200)
        self.assertEqual(
            self.client.delete(
                reverse("review-detail", args=[review_id])
            ).status_code,
            204,
        )

    def test_user_can_leave_multiple_reviews_for_completed_tours(self):
        Booking.objects.create(
            user=self.user,
            tour=self.tour,
            scheduled_at=timezone.now() - timedelta(days=1),
            status=Booking.Status.COMPLETED,
        )

        for comment in ("Первый отзыв", "Еще один отзыв"):
            response = self.client.post(
                reverse("review-list"),
                {
                    "user": self.user.pk,
                    "tour": self.tour.pk,
                    "rating": 5,
                    "comment": comment,
                },
                format="json",
            )
            self.assertEqual(response.status_code, 201)

        self.assertEqual(
            Review.objects.filter(user=self.user, tour=self.tour).count(),
            2,
        )

    def test_review_requires_completed_booking(self):
        response = self.client.post(
            reverse("review-list"),
            {
                "user": self.user.pk,
                "tour": self.tour.pk,
                "rating": 5,
                "comment": "Еще не был на туре",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.objects.count(), 0)

    def test_review_rating_must_be_between_one_and_five(self):
        Booking.objects.create(
            user=self.user,
            tour=self.tour,
            scheduled_at=timezone.now() - timedelta(days=1),
            status=Booking.Status.COMPLETED,
        )

        for rating in (0, 6):
            with self.subTest(rating=rating):
                response = self.client.post(
                    reverse("review-list"),
                    {
                        "user": self.user.pk,
                        "tour": self.tour.pk,
                        "rating": rating,
                        "comment": "Оценка вне допустимого диапазона",
                    },
                    format="json",
                )
                self.assertEqual(response.status_code, 400)
