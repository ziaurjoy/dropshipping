from rest_framework import serializers
from products_app.models import SettingExchangeRate, Category, Subcategory, Item, SearchSuggestion

class SettingExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingExchangeRate
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class SubcategorySerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Subcategory
        fields = ['id', 'category', 'name', 'items']

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'category_id', 'name', 'icon', 'subcategories']


class SearchSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchSuggestion
        fields = ['id', 'keyword']