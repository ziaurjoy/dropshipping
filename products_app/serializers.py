from rest_framework import serializers
from products_app.models import SettingExchangeRate

class SettingExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingExchangeRate
        fields = '__all__'