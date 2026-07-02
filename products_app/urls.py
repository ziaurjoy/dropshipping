from django.urls import path
from rest_framework.routers import DefaultRouter
from products_app.views import (
    Categories1688ViewSet,
    ProductFrom1688ViewSet,
    CategoryViewSet,
    item_search_img_view
)

router = DefaultRouter()
router.register(r'product-from-1688', ProductFrom1688ViewSet, basename='product-from-1688')
# router.register(r'categories-from-1688', Categories1688ViewSet, basename='categories-from-1688')
router.register(r'categories', CategoryViewSet, basename='categories')

urlpatterns = [
    path('item-search-img/', item_search_img_view, name='item-search-img'),
    path('item_search_img/', item_search_img_view, name='item_search_img'),
] + router.urls