from django.contrib import admin
from . import models

# Register models for admin interface
@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'user_type', 'is_verified', 'is_active')
    list_filter = ('user_type', 'is_verified', 'is_active')
    search_fields = ('email', 'username')


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'company_name', 'store_name')
    search_fields = ('user__email', 'company_name')


@admin.register(models.OTPVerify)
class OTPVerifyAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'otp_type', 'is_verify', 'created_at')
    list_filter = ('otp_type', 'is_verify', 'created_at')
    search_fields = ('email', 'phone')

