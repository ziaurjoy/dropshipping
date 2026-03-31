from rest_framework.routers import DefaultRouter, path

from cart_app.views import CartView

router = DefaultRouter()

from django.urls import path, include

urlpatterns = router.urls


urlpatterns = [
    path("", CartView.as_view(), name="cart"),                    #
]