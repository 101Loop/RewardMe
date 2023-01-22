from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.urls import reverse

from accounts.serializers import UserMobileSerializer
from core.constants import RequestType
from core.flags import FlagSources
from transactions.forms import TransactionForm
from transactions.utils import index_render, handle_transaction, handle_otp, redirect_to_transaction_page


# TODO: Refactor and add tests


def index(request: WSGIRequest):
    data = {}
    form = TransactionForm()
    if request.method == RequestType.POST:
        post_data = request.POST
        form = TransactionForm(request.POST)
        form.is_valid()

        if not FlagSources.otp_enabled():
            return redirect_to_transaction_page(request, post_data["username"])

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
                return index_render(request, data, form)

        serializer = UserMobileSerializer(data=post_data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data["redeem_points"] = post_data.get("redeem_points", False)
        # at this point flag is enabled
        data["otp_enabled"] = True

    return index_render(request, data, form)


def transact(request: WSGIRequest):
    user_id = request.session.get("user_id")
    if user_id is None:
        return redirect(reverse("transactions:index"))

    if request.method == RequestType.POST:
        return handle_transaction(request, user_id)

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
