from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Users
from .serializers import UserSerializer, SignUpSerializer


class SignUp(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = ()


class UsersList(generics.ListAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
