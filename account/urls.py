from django.urls import path
from .views import *
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token



urlpatterns = [
    path('register/', CreateAccountAPIView.as_view(), name="user-register"), # 회원가입 API 주소
    path('login/', obtain_jwt_token),
    path('verify/', verify_jwt_token),
    path('activate/<str:uidb64>/<str:token>', UserActivate.as_view(), name='activate'),
    path('findpassword/', FindPasswordApi.as_view()),
    path('verify/<str:uidb64>/<str:token>', ResetPasswordToken.as_view()),
    path('reset/', ResetPasswordApi.as_view())
]