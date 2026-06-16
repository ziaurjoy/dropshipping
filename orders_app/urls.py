from rest_framework.routers import DefaultRouter
from .views import (CouponViewSet, PaymentViewSet, ShipmentViewSet,
    ShippingMethodViewSet, ShippingZoneViewSet, SupportTicketViewSet, OrderViewSet)

router = DefaultRouter()
# router.register(r'orders', OrderViewSet, basename='order')
# router.register(r'addresses', DeliveryAddressViewSet, basename='deliveryaddress')
router.register(r'orders', OrderViewSet, basename='order')

router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'shipping-zones', ShippingZoneViewSet, basename='shippingzone')
router.register(r'shipments', ShipmentViewSet, basename='shipment')
router.register(r'shipment-method', ShippingMethodViewSet, basename='shipment-method')
router.register(r'support-tickets', SupportTicketViewSet, basename='supportticket')

urlpatterns = router.urls

