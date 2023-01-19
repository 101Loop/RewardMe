from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager, AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import gettext_lazy as _

from core.models import TimeStampedModel
from core.utils import random_number_token
from core.validators import MobileNumberValidator


class User(TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    # username will be user's mobile number
    username = models.CharField(
        verbose_name=_("Mobile Number"),
        max_length=10,
        unique=True,
    )
    email = models.EmailField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    objects = UserManager()

    def __str__(self):
        return str(self.username)

    def save(self, *args, **kwargs):
        validator = MobileNumberValidator()
        validator(self.username)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class OTPValidation(TimeStampedModel):
    # if otp is validated, set this to null
    otp = models.CharField(verbose_name=_("OTP"), max_length=6, null=True, blank=True)
    valid_until = models.DateTimeField(
        default=timezone.now,
        help_text="The timestamp of the moment of expiry of the saved token.",
    )
    destination = models.CharField(
        verbose_name=_("OTP Generated For"),
        max_length=10,
        db_index=True,
        unique=True,
    )
    is_validated = models.BooleanField(default=False)
    validate_attempt = models.IntegerField(verbose_name=_("Attempted Validation"), default=3)
    # if validate attempt reached 0 then, stop user to create new otp for 24 hours
    otp_reactive_at = models.DateTimeField(verbose_name=_("OTP Reactive At"), null=True, blank=True)
    extra_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.destination

    def generate_otp(self, length=6, valid_secs=600) -> None:
        """
        Generates a token of the specified length, then sets it on the model
        and sets the expiration of the token on the model.
        Pass 'commit=False' to avoid calling self.save().
        :param int length: Number of decimal digits in the generated token.
        :param int valid_secs: Amount of seconds the token should be valid.
        """
        otp = random_number_token(length)
        self.otp = otp
        self.valid_until = timezone.now() + timedelta(seconds=valid_secs)
        self.save(update_fields=["otp", "valid_until"])

        self._send_otp(f"Here's your OTP, {otp}", "1234567890", [self.destination])

    def verify_otp(self, otp):
        """
        Verifies a token by content and expiry.
        On success, the token is cleared and the device saved.
        :param str otp: The OTP token provided by the user.
        :rtype: bool
        """
        now_ = timezone.now()

        if self.otp is None or otp != self.otp or now_ >= self.valid_until:
            raise ValidationError("Invalid OTP Provided. Please try again.")

        self.token = None
        self.valid_until = now_
        self.save(update_fields=["otp", "valid_until"])
        return True

    def _send_otp(self, message, sms_from, sms_to: list[str]):
        from sms import send_sms

        send_sms(message, sms_from, sms_to)
