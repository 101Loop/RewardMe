from rest_framework import serializers

from accounts.models import User, OTPValidation
from core.validators import MobileNumberValidator


class UserMobileSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=10, required=True)

    def validate_username(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Mobile number must be digits")

        validator = MobileNumberValidator()
        validator(value)

        return value

    def validate(self, attrs):
        # get or create user here
        mobile = attrs["username"]
        try:
            User.objects.get(username=mobile)
        except User.DoesNotExist:
            User.objects.create_user(username=mobile)

        attrs["submit_otp"] = True
        self._generate_otp(mobile)

        return attrs

    def _generate_otp(self, mobile):
        otp_valdation_obj, _ = OTPValidation.objects.get_or_create(destination=mobile)
        otp_valdation_obj.generate_otp()

    class Meta:
        fields = ("username",)
