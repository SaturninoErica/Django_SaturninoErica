import secrets
from pathlib import Path

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import CaptchaLoginForm, RegistrationForm


def issue_captcha(request):
    left = secrets.randbelow(9) + 1
    right = secrets.randbelow(9) + 1
    request.session["captcha_answer"] = str(left + right)
    question = f"{left} + {right} = ?"
    request.session["captcha_question"] = question
    return question


def home(request):
    return redirect("account" if request.user.is_authenticated else "login")


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("account")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("login")
    return render(request, "accounts/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("account")

    if request.method == "POST":
        captcha_answer = request.session.pop("captcha_answer", None)
        request.session.pop("captcha_question", None)
        form = CaptchaLoginForm(
            request.POST, request=request, captcha_answer=captcha_answer
        )
        if form.is_valid():
            login(request, form.get_user())
            return redirect("account")
    else:
        form = CaptchaLoginForm(request=request)

    captcha_question = issue_captcha(request)
    return render(
        request,
        "accounts/login.html",
        {"form": form, "captcha_question": captcha_question},
    )


@login_required
def account(request):
    return render(request, "accounts/account.html")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


@staff_member_required
def test_report(request):
    report_path = Path(settings.TEST_REPORT_PATH)
    if not report_path.is_file():
        raise Http404("Отчет о тестировании пока не создан.")
    return FileResponse(
        report_path.open("rb"),
        as_attachment=True,
        filename="test-results.docx",
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
    )
