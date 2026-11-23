import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


class AccountFlowTests(TestCase):
    def setUp(self):
        self.password = "A-valid-password-839!"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.password,
        )

    def register_payload(self, **overrides):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "A-valid-password-839!",
            "password2": "A-valid-password-839!",
        }
        payload.update(overrides)
        return payload

    def test_registration_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("register"), self.register_payload()
        )

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("register"),
            self.register_payload(password2="a-different-password"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_login_page_displays_captcha_challenge(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertRegex(response.context["captcha_question"], r"^\d+ \+ \d+ = \?$")
        self.assertIn("captcha_answer", self.client.session)

    def test_login_rejects_incorrect_captcha(self):
        self.client.get(reverse("login"))
        response = self.client.post(
            reverse("login"),
            {
                "username": self.user.username,
                "password": self.password,
                "captcha": "incorrect",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertIn("captcha", response.context["form"].errors)

    def test_login_rejects_missing_captcha_challenge(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": self.user.username,
                "password": self.password,
                "captcha": "10",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertIn("captcha", response.context["form"].errors)

    def test_login_succeeds_with_correct_captcha_and_password(self):
        self.client.get(reverse("login"))
        answer = self.client.session["captcha_answer"]
        response = self.client.post(
            reverse("login"),
            {
                "username": self.user.username,
                "password": self.password,
                "captcha": answer,
            },
        )

        self.assertRedirects(response, reverse("account"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertNotIn("captcha_answer", self.client.session)

    def test_login_rejects_incorrect_password_with_valid_captcha(self):
        self.client.get(reverse("login"))
        answer = self.client.session["captcha_answer"]
        response = self.client.post(
            reverse("login"),
            {
                "username": self.user.username,
                "password": "incorrect-password",
                "captcha": answer,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertIn("__all__", response.context["form"].errors)

    def test_personal_account_requires_login(self):
        response = self.client.get(reverse("account"))

        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('account')}"
        )

    def test_authenticated_user_can_view_personal_account(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("account"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.email)

    def test_staff_can_download_word_test_report(self):
        self.user.is_staff = True
        self.user.save(update_fields=["is_staff"])
        self.client.force_login(self.user)

        with tempfile.TemporaryDirectory() as temporary_directory:
            report_path = Path(temporary_directory) / "test-results.docx"
            report_path.write_bytes(b"test report")
            with override_settings(TEST_REPORT_PATH=report_path):
                response = self.client.get(reverse("test-report"))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response["Content-Type"],
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document",
                )
                self.assertIn("attachment", response["Content-Disposition"])
                response.close()

    def test_non_staff_cannot_download_word_test_report(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("test-report"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])
