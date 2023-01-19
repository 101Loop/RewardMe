from django.urls import path

from transactions.views import index, transact

app_name = "transactions"

urlpatterns = [
    path("", index, name="index"),
    path("transact/", transact, name="transact"),
]
