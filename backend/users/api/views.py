from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserProfileSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Возвращает данные о текущем пользователе."""
        user = request.user
        serializer = UserProfileSerializer(user, context={"request": request})
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """Обновляет данные профиля текущего пользователя."""
        user = request.user
        serializer = UserProfileSerializer(
            user, data=request.data, partial=True, context={"request": request}
        )  # partial=True для частичного обновления
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
