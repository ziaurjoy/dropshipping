from rest_framework import serializers
from products_app.models import SettingExchangeRate, Category, Subcategory, SearchSuggestion

class SettingExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingExchangeRate
        fields = '__all__'

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'category_id', 'name', 'icon', 'subcategories']


class SearchSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchSuggestion
        fields = ['id', 'keyword']