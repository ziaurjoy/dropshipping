

from rest_framework.routers import DefaultRouter
from .views import (BannerViewSet, CategoryViewSet, ProductImageViewSet, ProductVariantViewSet,
    ProductViewSet, ReviewViewSet, SupplierProductViewSet, WishlistViewSet)

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

router.register(r'variants', ProductVariantViewSet, basename='product-variant')
router.register(r'images', ProductImageViewSet, basename='product-image')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'supplier-products', SupplierProductViewSet, basename='supplierproduct')





urlpatterns = router.urls