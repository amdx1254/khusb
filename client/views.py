from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
import requests,json
import urllib
from django.conf import settings
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

def check_auth(request):
    if(not 'token' in request.session):
        return False
    r = requests.post('http://127.0.0.1:8000/api/verify/', data={'token' : request.session['token']}).json()
    if('non_field_errors' in r):
        del request.session['token']
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
        # 하나라도 비어있을 경우 오류 출력
        if(username == '' or password == ''):
            return render(request, 'client/register.html',{'data':"제대로 입력하세요"})
        if(password != password_conf):
            return render(request, 'client/register.html',{'data':'패스워드가 일치하지 않습니다.'})
        # API 서버에 회원가입API에 post로 request보냄.
        r = requests.post('http://127.0.0.1:8000/api/register/', data={'email':email,'username':username, 'password':password})

        if(r.text.find(email)>0):
            r = requests.post('http://127.0.0.1:8000/api/login/',
                              data={'email': email, 'password': password}).json()
            print(r)
            request.session['token'] = r['token']

            return redirect('list-view')

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
        request.session['token'] = token
        return redirect('list-view')


def LoginView(request):
    if(check_auth(request)):
        return redirect('list-view')

    if(request.method == 'GET'):
        if('token' in request.session):
            return redirect('list-view')
        return render(request, 'client/login.html')

    if(request.method == 'POST'):
        email = request.POST['email']
        pwd = request.POST['password']
        r = requests.post('http://127.0.0.1:8000/api/login/', data={'email':email,'password':pwd}).json()

        if('non_field_errors' in r):
            return render(request, 'client/login.html', {'data':'일치하는 정보가 없습니다'})
        request.session['token']=r['token']

        return redirect('list-view')


@csrf_exempt
def listView(request,path='/'):
    if(path!='/'):
        path='/'+path+"/"
    if(not check_auth(request)):
        return redirect('user-login')
    if(request.method == 'GET'):
        r = {}
        r['path'] = path
        r['token']=request.session['token']
        r['username'] = request.user.username
        return render(request, 'client/main.html', r)


@csrf_exempt
def shareView(request):
    if(not check_auth(request)):
        return redirect('user-login')
    if(request.method == 'GET'):
        r = {}
        r['path'] = "/Shared Folder"
        r['token'] = request.session['token']
        r['username'] = request.user.username
        return render(request, 'client/share.html', r)


def DownloadView(request, path):
    path = '/'+path
    if(not check_auth(request)):
        return redirect('user-login')
    if(request.method == 'GET'):
        error=''
        if 'error' in request.GET:
            error = request.GET['error']
        id = request.GET.get('id','')
        if(id != ''):
            r = requests.get('http://127.0.0.1:8000/api/downloadshare/?id='+id,
                             headers={'Authorization': 'Bearer ' + request.session['token']}).json()
        else:
            r = requests.get('http://127.0.0.1:8000/api/download'+path, headers={'Authorization': 'Bearer '+ request.session['token'] }).json()
        print("DOWNLOADED",r)
        if('error' in r):
            return redirect('list-view')
        return HttpResponseRedirect(r['url'])


def LogoutView(request):
    logout(request)
    return redirect('user-login')
