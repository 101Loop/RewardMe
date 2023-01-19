from django.db import transaction as db_transaction
from django.db.models import F
from rest_framework import serializers
from simple_history.utils import update_change_reason

from accounts.models import User
from transactions.constants import PaymentType
from transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if attrs["payment_amount"] > attrs["invoice_amount"]:
            raise serializers.ValidationError("Payment amount cannot be greater than invoice amount")

        if attrs["payment_type"] == PaymentType.POINTS and attrs["payment_amount"] != 0:
            raise serializers.ValidationError("Payment amount should be 0 for payment type as points.")

        user = User.objects.select_related("reward_points").get(id=self.context["user_id"])
        attrs["user"] = user
        return attrs

    class Meta:
        model = Transaction
        fields = ["product_type", "invoice_amount", "payment_amount", "payment_type", "note"]

    def create(self, validated_data):
        redeemed_points = 0
        payment_amount = validated_data["payment_amount"]
        if is_points_redeemed := self.context.get("is_points_redeemed", False):
            redeemed_points = int(validated_data["invoice_amount"] - payment_amount)
            validated_data["redeemed_points"] = redeemed_points
            validated_data["is_points_redeemed"] = is_points_redeemed

        return self._create_transaction(validated_data, payment_amount, redeemed_points)

    def _create_transaction(self, validated_data, payment_amount, redeemed_points):
        # everything should be in atomic transaction
        with db_transaction.atomic():
            # deduct points from user's reward points
            user = validated_data["user"]
            # for now let's assume every 100 rupee spent, 1 point is earned
            points_earned = payment_amount // 100
            user.reward_points.points = F("points") - redeemed_points + points_earned
            user.reward_points.save()
            validated_data["points_earned"] = points_earned
            transaction: Transaction = Transaction.objects.create(**validated_data)
            # change reason
            update_change_reason(
                user.reward_points,
                f"Points redeemed for transaction. Transaction ID: {transaction.id}. Points redeemed: {redeemed_points}. Points earned: {points_earned}",
            )
            return transaction
