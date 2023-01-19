from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.urls import reverse

from accounts.models import OTPValidation
from accounts.serializers import UserMobileSerializer
from transactions.forms import TransactionForm
from transactions.models import RewardPoints
from transactions.serializers import TransactionSerializer


# TODO: Refactor and add tests


def _index_render(request: WSGIRequest, data, form):
    return render(
        request,
        "index.html",
        {
            "submit_otp": data.get("submit_otp"),
            "mobile": data.get("username"),
            "redeem_points": data.get("redeem_points"),
            "form": form,
        },
    )


def index(request: WSGIRequest):
    data = {}
    form = TransactionForm()
    if request.method == "POST":
        post_data = request.POST
        form = TransactionForm(request.POST)

        if "otp" in post_data:
            try:
                return handle_otp(request, post_data["username"], post_data["otp"])
            except ValidationError as e:
                form.add_error(None, e)
                data |= {
                    "submit_otp": True,
                    "username": post_data["username"],
                    "redeem_points": post_data.get("redeem_points", False),
                }
                # TODO: after 3 failed attempts, redirect to index
                # TODO: maybe give option to generate new otp
                return _index_render(request, data, form)

        serializer = UserMobileSerializer(data=post_data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data["redeem_points"] = post_data.get("redeem_points", False)

    return _index_render(request, data, form)


def handle_otp(request: WSGIRequest, destination, otp):
    otp_validation = OTPValidation.objects.get(destination=destination)
    otp_validation.verify_otp(otp)

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


def transact(request):
    user_id = request.session.get("user_id")
    if user_id is None:
        return redirect(reverse("transactions:index"))

    if request.method == "POST":
        return _handle_transaction(request, user_id)

    if not (product_type := request.session.pop("product_type", None)):
        return redirect(reverse("transactions:index"))
    invoice_amount = request.session.pop("invoice_amount", None)
    payment_amount = invoice_amount
    points = 0
    if redeem_points := request.session.get("redeem_points"):
        points = request.session.pop("points", 0)
        invoice_amount = Decimal(invoice_amount)
        if points > invoice_amount:
            # maybe a user can accumulate points and use them later
            # at that point of time points can be more than invoice amount
            payment_amount = Decimal(0)
        else:
            payment_amount = invoice_amount - points

    form = TransactionForm(
        initial={
            "product_type": product_type,
            "invoice_amount": invoice_amount,
            "payment_amount": payment_amount,
        }
    )

    if points > 0:
        if redeem_points:
            messages.add_message(
                request,
                messages.INFO,
                f"Hello, initially you had {points} points. Points will be adjusted in your payment amount. "
                f"You need to pay ₹{payment_amount}.",
            )
        else:
            messages.add_message(
                request, messages.INFO, f"Hello, you have {points} points. You can save money by redeeming them."
            )
    return render(request, "transact.html", {"form": form})


def _handle_transaction(request, user_id):
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
