from django.contrib.auth import authenticate, logout, login
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UserSerializer, CreateUserSerializer


class CreateUserView(GenericAPIView):
    """
    Registration user
    ---
        {
            "username": "p1",
            "password": "123qwe123",
            "password_2": "123qwe123",
            "role": "partner",
        }
    ---
    """
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data,
                        status=status.HTTP_201_CREATED)


@api_view(['POST'])
def sign_in(request):
    """
    ---
        {
            "username": "p1",
            "password": "123qwe123"
        }
    ---
    """
    username = request.data.get('username', False)
    password = request.data.get('password', False)

    if not username or not isinstance(username, str):
        return Response({'error': {'username': 'empty username'}},
                        status=400)
    if not password:
        return Response({'error': {'password': 'empty password'}},
                        status=400)
    user = authenticate(
        username=username, password=password
    )
    if request.user.is_authenticated:
        if request.user != user:
            logout(request)

    if user:
        login(request, user)
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
    else:
        return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)


class UserView(GenericAPIView):
    """
    Get user information
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        return Response(self.get_serializer(request.user).data,
                        status=status.HTTP_200_OK)
