from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("account/", views.account, name="account"),
    path("logout/", views.logout_view, name="logout"),
    path("test-report/", views.test_report, name="test-report"),
]
