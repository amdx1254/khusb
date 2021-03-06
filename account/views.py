import traceback
from django.shortcuts import redirect
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, permissions

from account.tokens import account_activation_token
from .models import User
from .serializers import AccountSerializer
from rest_framework.views import APIView, Response
from rest_framework import status
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.conf import settings

class CreateAccountAPIView(APIView):
    permission_classes = (permissions.AllowAny, )
    def post(selfself, request):
        exist_user = User.objects.filter(email=request.data['email'])
        if(exist_user.exists()):
            print("EXIST?")
            if(exist_user[0].active==False):
                exist_user[0].delete()
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(email=request.data['email'])
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = account_activation_token.make_token(user)
            domain = settings.DOMAIN
            message = user.username + "님 아래 링크를 클릭해서 계정을 활성화 해주세요.\n" + "http://"+domain+"/activate/" + uid + "/" + token
            to_email = request.data['email']
            mail_subject = 'KHUSB email verification'
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FindPasswordApi(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(selfself, request):
        try:
            user = User.objects.get(email=request.data['email'])
            serializer = AccountSerializer(user)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = account_activation_token.make_token(user)
            domain = settings.DOMAIN
            message = user.username + "님 아래 링크를 클릭해서 비밀번호를 변경해주세요.\n" + "http://"+domain+"/verify/" + uid + "/" + token
            to_email = request.data['email']
            mail_subject = 'KHUSB email verification'
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"status":"error","data":"User Not Exist"}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordApi(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        current_pass = request.data['current_password']
        password = request.data['password']
        password_conf = request.data['password_conf']

        if(not request.user.check_password(current_pass)):
            return Response({'status': 'failed', 'result': '잘못된 패스워드 입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if(password != password_conf):
            return Response({'status': 'failed', 'result': '패스워드가 일치하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(password)
        request.user.save()
        return Response({'status': 'success', 'result': '패스워드가 변경되었습니다.'}, status=status.HTTP_200_OK)


class ResetPasswordToken(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        try:
            if user is not None and account_activation_token.check_token(user, token):
                user.set_password(request.data["password"])
                user.save()
                return Response({"status":"success","result": "이메일 변경 완료."}, status=status.HTTP_200_OK)
            else:
                return Response({'status':'failed','result': '만료된 링크입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(traceback.format_exc())


class UserActivate(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        try:
            if user is not None and account_activation_token.check_token(user, token):
                user.active = True
                user.save()
                return Response({"status":"success","result": user.email + " 계정이 활성화 되었습니다."}, status=status.HTTP_200_OK)
            else:
                return Response({'status':'failed','result':'만료된 링크입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(traceback.format_exc())


