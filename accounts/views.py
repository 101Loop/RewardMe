from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import UserMobileSerializer


class UserAPIView(APIView):
    def post(self, request, format=None):
        serializer = UserMobileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        is_new = data["is_new"]
        if is_new:
            return redirect(
                reverse("transactions:transact") + f"?points={data['points']}",
                permanent=True,
            )

        if not is_new:
            return redirect(reverse("transactions:index") + f"?submit_otp=true")
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
