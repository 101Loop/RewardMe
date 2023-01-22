from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.urls import reverse

from accounts.models import OTPValidation
from transactions.models import RewardPoints
from transactions.serializers import TransactionSerializer


def index_render(request: WSGIRequest, data, form):
    return render(
        request,
        "index.html",
        {
            "submit_otp": data.get("submit_otp"),
            "mobile": data.get("username"),
            "redeem_points": data.get("redeem_points"),
            "otp_enabled": data.get("otp_enabled"),
            "form": form,
        },
    )


def handle_otp(request: WSGIRequest, destination: str, otp: str):
    otp_validation = OTPValidation.objects.get(destination=destination)
    otp_validation.verify_otp(otp)

    return redirect_to_transaction_page(request, destination)


def redirect_to_transaction_page(request: WSGIRequest, destination: str):
    reward_point = RewardPoints.objects.values("points", "user_id").get(user__username=destination)
    # we'll keep points in session
    request.session.update(
        {
            "user_id": str(reward_point["user_id"]),
            "points": reward_point["points"],
            "product_type": request.POST.get("product_type"),
            "invoice_amount": request.POST.get("invoice_amount"),
            "redeem_points": request.POST.get("redeem_points", False),
        }
    )
    return redirect(reverse("transactions:transact"))


def handle_transaction(request: WSGIRequest, user_id: str):
    serializer = TransactionSerializer(
        data=request.POST,
        context={"user_id": user_id, "is_points_redeemed": bool(request.session.get("redeem_points"))},
    )
    serializer.is_valid(raise_exception=True)
    serializer.create(serializer.validated_data)
    # remove session so that user can't go back to transact page
    request.session.pop("user_id")
    # get the latest points
    points = RewardPoints.objects.values("points").get(user_id=user_id)["points"]
    return render(request, "success.html", {"points": points})
