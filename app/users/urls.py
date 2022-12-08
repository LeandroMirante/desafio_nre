from django.urls import include, path
from app.users import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"company", views.CompanyViewSet)
router.register(r"customer", views.CustomerViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", views.LoginAPIView.as_view(), name="login"),
    path(
        "auth/request-reset-email/",
        views.RequestPasswordResetEmail.as_view(),
        name="request-reset-email",
    ),
    path(
        "auth/password-reset/<uidb64>/<token>/",
        views.PasswordTokenCheckAPI.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "auth/password-reset-complete",
        views.SetNewPasswordAPIView.as_view(),
        name="password-reset-complete",
    ),
    path(
        "change-password/",
        views.ChangePasswordView.as_view(),
        name="change-password-confirm",
    ),
]
