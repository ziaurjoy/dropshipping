from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet, CouponViewSet,
    PaymentViewSet, ShippingZoneViewSet,
    ShipmentViewSet, SupportTicketViewSet
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
# router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'shipping-zones', ShippingZoneViewSet, basename='shippingzone')
router.register(r'shipments', ShipmentViewSet, basename='shipment')
router.register(r'support-tickets', SupportTicketViewSet, basename='supportticket')

urlpatterns = router.urls