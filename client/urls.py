from django.urls import path
from django.conf.urls import url
from . import views
urlpatterns = [
    path('register/', views.CreateAccountView, name='user-signup'),
    path('activate/<str:uidb64>/<str:token>', views.ActivateView, name='activate'),
    path('findpassword/',views.FindPasswordView, name='find-password'),
    path('verify/<str:uidb64>/<str:token>', views.FindPasswordVerifyView, name='activate'),
    path('', views.LoginView, name='user-login'),
    path('login-social', views.SocialLoginView, name='social-login'),
    path('list/', views.listView, name='list-view'),
    path('list/<path:path>/', views.listView, name='list-view'),
    path('link/', views.LinkListView, name='link-view'),
    path('listshare/', views.shareView),
    path('listdoshare/', views.shareDoneView),
    path('logout/', views.LogoutView),
    path('download/',views.DownloadView),
    path('download/<path:path>/', views.DownloadView),
]