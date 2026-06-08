from django.contrib import admin

from products_app.models import Categories, SettingExchangeRate

# Register your models here.
admin.site.register(Categories)
admin.site.register(SettingExchangeRate)