
# from django.urls import path, include
# from rest_framework import routers

# from . import views

# # Routers provide an easy way of automatically determining the URL conf.
# router = routers.DefaultRouter()
# router.register(r"users", views.UsersViewSet, basename="user")


# urlpatterns = [
#     # ...
#     path("", include(router.urls)),
# ]



from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

urlpatterns = [
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("signup/", views.RegisterUserView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("otp-verified/", views.VerifyOTP.as_view(), name="otp-verified"),
    path("send-otp/", views.SendOTP.as_view(), name="otp-verified"),
    path(
        "change-password/", views.ChangePasswordView.as_view(), name="change-password"
    ),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path(
        "profile-update/", views.ProfileUpdateApiView.as_view(), name="reset-password"
    ),
    path("google/login/", views.GoogleLoginApiView.as_view(), name="google-login"),

]

router.register(r'delivery-addresses', views.DeliveryAddressViewSet, basename='deliveryaddress')
router.register(r'integration-credentials', views.IntegrationCredentialViewSet, basename='integrationcredential')



urlpatterns += router.urls
