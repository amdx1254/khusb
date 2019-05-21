from django.shortcuts import render
from rest_framework import generics, permissions
from .models import User
from .serializers import AccountSerializer
# Create your views here.

# CreateAPIView를 통해 post를 통해 입력 받은 값을 자동으로 AccountSerializer를 통해 생성시켜줌.
class CreateAccouuntAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = AccountSerializer
