from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Users
from .serializers import UserSerializer


@api_view(["GET"])
def users_list(request):
    users = Users.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def user_detail(request, pk):
    try:
        user = Users.objects.get(pk=pk)
    except Users.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = UserSerializer(user)
        return Response(serializer.data)
