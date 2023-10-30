from django.contrib.auth import authenticate, get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import GameUsers, Thread

User = get_user_model()


# Create your views here.
def home(request):
    return JsonResponse({'Test response': 'Done'})


def messages_page(request):
    threads = Thread.objects.by_user(user=request.user).order_by('timestamp')
    context = {
        'Threads': threads
    }
    # return render(request, 'messages.html', context)


class LoginView(APIView):
    def post(self, request):
        gender = request.POST["gender"]
        username = request.POST["username"]
        password = request.POST["password"]
        user = User.objects.get(username=username, password=password, gender=gender)
        if not user:
            return JsonResponse({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({f"User - {username}": {'token': str(token), 'created': created}})


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.user.username
        print(username)
        token = Token.objects.get(user=request.user)
        token.delete()
        return JsonResponse({"Success": f"User - {username} logged out"}, status=status.HTTP_200_OK)
