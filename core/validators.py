from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.text import gettext_lazy as _


@deconstructible
class MobileNumberValidator(validators.RegexValidator):
    # validator for indian mobile numbers
    regex = r"^[6-9]\d{9}$"
    message = _("Enter a valid mobile number.")
    flags = 0
