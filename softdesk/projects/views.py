from rest_framework import generics
from .models import Users
from .serializers import UserSerializer, SignUpSerializer


class SignUp(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = ()


class UsersList(generics.ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
