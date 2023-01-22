from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import RewardPoints, Transaction


@admin.register(RewardPoints)
class RewardPointsAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ("user_id", "points", "created_at")
    search_fields = ("user_id",)
    list_per_page = 25
    raw_id_fields = ["user"]


@admin.register(Transaction)
class TransactionAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ("user_id", "product_type", "invoice_amount", "payment_amount", "payment_type", "created_at")
    search_fields = ("user_id",)
    list_per_page = 25
    raw_id_fields = ["user"]
    list_filter = ("payment_type", "product_type", "is_points_redeemed")
