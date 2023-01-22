from django.contrib import admin

from accounts.models import User, OTPValidation


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff", "is_active", "is_superuser", "created_at")
    list_filter = ("is_active", "is_superuser")
    search_fields = ("username",)


@admin.register(OTPValidation)
class OTPValidationAdmin(admin.ModelAdmin):
    list_display = ("destination", "otp", "valid_until", "is_validated")
    list_filter = ("is_validated",)
    search_fields = ("destination",)

