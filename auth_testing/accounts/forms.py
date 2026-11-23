import hmac

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Электронная почта")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class CaptchaLoginForm(forms.Form):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    captcha = forms.CharField(label="Ответ на пример")

    def __init__(self, *args, request=None, captcha_answer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.captcha_answer = captcha_answer
        self.user_cache = None

    def clean_captcha(self):
        answer = self.cleaned_data["captcha"].strip()
        if self.captcha_answer is None or not hmac.compare_digest(
            answer, self.captcha_answer
        ):
            raise ValidationError("Неверный ответ CAPTCHA. Решите новый пример.")
        return answer

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        self.user_cache = authenticate(
            self.request,
            username=cleaned_data["username"],
            password=cleaned_data["password"],
        )
        if self.user_cache is None:
            raise ValidationError("Неверное имя пользователя или пароль.")
        return cleaned_data

    def get_user(self):
        return self.user_cache
