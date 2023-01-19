from django.urls import path

from accounts.views import UserAPIView

app_name = "accounts"

urlpatterns = [
    path("users/", UserAPIView.as_view(), name="users"),
]
