from django.urls import path
from .views import CreateAccouuntAPIView
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token



urlpatterns = [
    path('register/', CreateAccouuntAPIView.as_view(), name="user-register"), # 회원가입 API 주소
    path('login/', obtain_jwt_token),
    path('verify/', verify_jwt_token),
]