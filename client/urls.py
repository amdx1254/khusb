from django.urls import path
from django.conf.urls import url
from . import views
urlpatterns = [
    path('register/', views.CreateAccountView, name='user-signup'), #  회원가입 템플릿
    path('', views.LoginView, name='user-login'),
    path('login-social', views.SocialLoginView, name='social-login'),
    path('list/', views.listView, name='list-view'),
    path('list/<path:path>/', views.listView, name='list-view'),
    path('logout/',views.LogoutView),
    path('download/',views.DownloadView),
    path('download/<path:path>/', views.DownloadView),
]