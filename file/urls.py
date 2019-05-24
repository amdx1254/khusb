from django.urls import path
from .views import *
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token



urlpatterns = [
    path('create/', FolderCreateApi.as_view(), name="user-register"), # 회원가입 API 주소
    path('list/', FolderListApi.as_view()),
    path('list/<path:path>/', FolderListApi.as_view()),
    path('upload/', FileCreateApi.as_view()),
    path('download/', FileDownloadApi.as_view()),
    path('download/<path:path>/', FileDownloadApi.as_view()),
    path('delete/',FileDeleteApi.as_view())
]