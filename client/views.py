from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
import requests,json
import urllib
from django.conf import settings
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import logout, authenticate, login
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import permission_required
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

def check_auth(request):
    if(request.COOKIES.get('khusb_token') == None):
        return False
    r = requests.post('http://127.0.0.1:8000/api/verify/', data={'token' : request.COOKIES.get('khusb_token')}).json()
    if('non_field_errors' in r):
        return False
    return True


def CreateAccountView(request):
    if(check_auth(request)):
        return redirect('list-view')
    if(request.method == 'GET'):
        return render(request, 'client/register.html')

    elif(request.method=='POST'):
        username = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        password_conf = request.POST['password_conf']
        settings.DOMAIN = request.META['HTTP_HOST']
        # 하나라도 비어있을 경우 오류 출력
        if(username == '' or password == ''):
            return render(request, 'client/register.html',{'data':"제대로 입력하세요"})
        if(password != password_conf):
            return render(request, 'client/register.html',{'data':'패스워드가 일치하지 않습니다.'})
        # API 서버에 회원가입API에 post로 request보냄.
        r = requests.post('http://127.0.0.1:8000/api/register/', data={'email':email,'username':username, 'password':password})

        if(r.text.find(email)>0):
            return render(request, 'client/register.html', {'data': '인증 메일을 ' + email + '로 전송하였습니다.'})

        elif(r.text.find("A user with that username")>0):
            return render(request, 'client/register.html', {'data': '존재하는 ID 입니다.'})
        elif(r.text.find('Email is already in use')>0):
            return render(request, 'client/register.html', {'data':'이미 존재하는 Email입니다.'})
        elif(r.text.find('Enter a valid email')>0):
            return render(request, 'client/register.html', {'data': '올바른 이메일을 입력하세요.'})
        elif(r.text.find('Enter a valid username')>0):
            return render(request, 'client/register.html', {'data': '올바른 아이디를 입력하세요.'})



        return render(request, 'client/register.html', {'data': r.text})


def SocialLoginView(request):
    if(request.method == 'GET'):
        print(request.user.email)
        payload = jwt_payload_handler(request.user)
        token = jwt_encode_handler(payload)
        response = redirect('list-view')
        response.set_cookie('khusb_token',token)
        return response


def LoginView(request):
    if(check_auth(request)):
        return redirect('list-view')

    if(request.method == 'GET'):
        return render(request, 'client/login.html')

    if(request.method == 'POST'):
        email = request.POST['email']
        pwd = request.POST['password']
        if(email == '' or pwd == ''):
            return render(request, 'client/login.html', {'data': '일치하는 정보가 없습니다'})

        r = requests.post('http://127.0.0.1:8000/api/login/', data={'email':email,'password':pwd}).json()

        if('non_field_errors' in r):
            return render(request, 'client/login.html', {'data':'일치하는 정보가 없습니다'})

        user = authenticate(email=email, password=pwd)
        if(user.active == False):
            return render(request, 'client/login.html', {'data':'인증이 완료되지 않은 계정입니다.'})
        if(user != None):
            print("LOGON")
            login(request, user)
        response = redirect('list-view')
        response.set_cookie('khusb_token',r['token'], max_age=86400)
        return response


def ActivateView(request, uidb64, token):

    r = requests.get('http://127.0.0.1:8000/api/activate/'+uidb64+'/'+token).json()
    print(r)
    if(r['status'] == 'success'):
        return render(request, 'client/activate.html', {'data': '계정이 활성화되었습니다'})
    else:
        return render(request,'client/activate.html', {'data': '만료된 링크입니다'})




@csrf_exempt
def listView(request,path='/'):
    if(not check_auth(request)):
        response = redirect('user-login')
        response.delete_cookie('khusb_token')
        return response
    if(path!='/'):
        path='/'+path+"/"
    if(request.method == 'GET'):
        r = {}
        r['path'] = path
        r['username'] = request.user.username
        return render(request, 'client/main.html', r)


@csrf_exempt
def shareView(request):
    if(not check_auth(request)):
        response = redirect('user-login')
        response.delete_cookie('khusb_token')
        return response
    if(request.method == 'GET'):
        r = {}
        r['path'] = "/Shared Folder"
        r['username'] = request.user.username
        return render(request, 'client/share.html', r)


@csrf_exempt
def shareDoneView(request):
    if(not check_auth(request)):
        response = redirect('user-login')
        response.delete_cookie('khusb_token')
        return response
    if(request.method == 'GET'):
        r = {}
        r['path'] = "/Shared Folder"
        r['username'] = request.user.username
        return render(request, 'client/listsharedone.html', r)


def DownloadView(request, path):
    path = '/'+path
    if(not check_auth(request)):
        response = redirect('user-login')
        response.delete_cookie('khusb_token')
        return response
    if(request.method == 'GET'):
        error=''
        if 'error' in request.GET:
            error = request.GET['error']
        id = request.GET.get('id','')
        if(id != ''):
            r = requests.get('http://127.0.0.1:8000/api/downloadshare/?id='+id,
                             headers={'Authorization': 'Bearer ' + request.COOKIES.get('khusb_token')}).json()
        else:
            r = requests.get('http://127.0.0.1:8000/api/download'+path, headers={'Authorization': 'Bearer '+ request.COOKIES.get('khusb_token')}).json()
        print("DOWNLOADED",r)
        if('error' in r):
            return redirect('list-view')
        return HttpResponseRedirect(r['url'])


def LogoutView(request):
    logout(request)
    response = redirect('user-login')
    response.delete_cookie('khusb_token')
    return response
