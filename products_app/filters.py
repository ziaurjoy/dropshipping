import django_filters
from .models import Product, Category

class ProductFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    min_price = django_filters.NumberFilter(field_name='variants__selling_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='variants__selling_price', lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(field_name='variants__stock_quantity', lookup_expr='gt', distinct=True)

    class Meta:
        model = Product
        fields = ['category', 'is_active']