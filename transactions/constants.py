from django.db.models import TextChoices


class ProductCategory(TextChoices):
    MOTOR_CYCLE = "motorcycle", "Motorcycle"
    AUTO = "auto", "Auto"
    TRUCK = "truck", "Truck"
    CAR = "car", "Car"


class PaymentType(TextChoices):
    CASH = "cash", "Cash"
    NEFT = "neft", "NEFT"
    RTGS = "rtgs", "RTGS"
    IMPS = "imps", "IMPS"
    UPI = "upi", "UPI"
    PAYTM = "paytm", "Paytm"
    POINTS = "points", "Points"
