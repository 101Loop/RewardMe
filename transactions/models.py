from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.text import gettext_lazy as _
from simple_history.models import HistoricalRecords

from core.models import TimeStampedModel
from transactions.constants import ProductCategory, PaymentType

User = get_user_model()


class RewardPoints(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="reward_points")
    points = models.PositiveBigIntegerField(default=0)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Reward Point")
        verbose_name_plural = _("Reward Points")

    def __str__(self):
        return f"{self.user} - {self.points}"


class Transaction(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    product_type = models.CharField(max_length=50, choices=ProductCategory.choices)
    # total amount of transaction
    invoice_amount = models.DecimalField(max_length=10, decimal_places=2, max_digits=10)
    # amount of transaction after redeeming points
    payment_amount = models.DecimalField(max_length=10, decimal_places=2, max_digits=10)
    payment_type = models.CharField(max_length=50, choices=PaymentType.choices)
    invoice_date = models.DateTimeField(db_index=True, editable=False, default=timezone.now)
    note = models.TextField(blank=True, null=True)
    is_points_redeemed = models.BooleanField(default=False)
    # these are the points which are being redeemed for this transaction
    redeemed_points = models.PositiveBigIntegerField(default=0)
    points_earned = models.PositiveBigIntegerField(default=0)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user} - {self.payment_amount}"

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    def calculate_reward_points(self):
        pass
