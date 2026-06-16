from rest_framework.routers import DefaultRouter, path

from cart_app.views import CartViewSet

# from cart_app.views import CartView

router = DefaultRouter()

from django.urls import path, include

router.register(r'', CartViewSet, basename='cart')

urlpatterns = router.urls







# urlpatterns = [
#     # path("", CartView.as_view(), name="cart"),
#     # path('', AddToCartView.as_view(), name='cart-add'),
#     path('', include(router.urls)),                  #
# ]