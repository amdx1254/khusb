from django.urls import path
from .views import *

urlpatterns = [
    path('create/', FolderCreateApi.as_view(), name="user-register"), # 회원가입 API 주소
    path('list/', FolderListApi.as_view()),
    path('list/<path:path>/', FolderListApi.as_view()),
    path('upload/', FileCreateApi.as_view()),
    path('download/', FileDownloadApi.as_view()),
    path('download/<path:path>/', FileDownloadApi.as_view()),
    path('delete/',FileDeleteApi.as_view()),
    path('move/', FileMoveApi.as_view()),
    path('copy/', FileCopyApi.as_view())
]