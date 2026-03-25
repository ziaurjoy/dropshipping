
from django.urls import path, include
from rest_framework import routers

from . import views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"users", views.UsersViewSet, basename="user")


urlpatterns = [
    # ...
    path("", include(router.urls)),
]
