from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
import requests,json
import urllib
from django.conf import settings
# Create your views here.
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
        username = request.POST['mbname']
        userid = request.POST['cursor:pointer']
        password = request.POST['mbpw']
        email = request.POST['email']+"@"+request.POST['email_dns']
        # 하나라도 비어있을 경우 오류 출력
        if(username == '' or userid == '' or password == ''):
            return render(request, 'client/register.html',{'data':"제대로 입력하세요"})
        # API 서버에 회원가입API에 post로 request보냄.
        r = requests.post('http://127.0.0.1:8000/api/register/', data={'userid':userid, 'username':username, 'password':password, 'email':email})



        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",r.text)
        if(r.text.find(userid)>0):
            r = requests.post('http://127.0.0.1:8000/api/login/',
                              data={'userid': userid, 'password': password}).json()
            request.session['token'] = r['token']

            return redirect('list-view')
            #return render(request, 'client/register.html', {'data':'가입 완료'})
        elif(r.text.find("A user with that username")>0):
            return render(request, 'client/register.html', {'data': '존재하는 ID 입니다.'})
        elif(r.text.find('Email is already in use')>0):
            return render(request, 'client/register.html', {'data':'이미 존재하는 Email입니다.'})
        elif(r.text.find('Enter a valid email')>0):
            return render(request, 'client/register.html', {'data': '올바른 이메일을 입력하세요.'})
        elif(r.text.find('Enter a valid username')>0):
            return render(request, 'client/register.html', {'data': '올바른 아이디를 입력하세요.'})



        return render(request, 'client/register.html', {'data': r.text})


def LoginView(request):
    if(check_auth(request)):
        return redirect('list-view')
    if(request.method == 'GET'):
        if('token' in request.session):
            return redirect('list-view')
        return render(request, 'client/login.html')

    if(request.method == 'POST'):
        userid = request.POST['id']
        pwd = request.POST['pwd1']
        r = requests.post('http://127.0.0.1:8000/api/login/', data={'userid':userid,'password':pwd}).json()

        if('non_field_errors' in r):
            return render(request, 'client/login.html', {'data':'일치하는 정보가 없습니다'})
        request.session['token']=r['token']

        return redirect('list-view')

def listView(request,path='/'):
    if(path!='/'):
        path='/'+path
    if(not check_auth(request)):
        return redirect('user-login')
    if(request.method == 'GET'):
        error=''
        if 'error' in request.GET:
            error = request.GET['error']
        r = requests.get('http://127.0.0.1:8000/api/list'+path, headers={'Authorization': 'Bearer '+ request.session['token'] }).json()
        r['error']=error
        parentpath = path[:path.rfind('/')]
        r['parent']=parentpath
        print(r)
        return render(request, 'client/list.html', r)

    if(request.method == 'POST'):
        # 폴더 생성 부분
        if('name' in request.POST):
            name = request.POST['name']
            r = requests.post('http://127.0.0.1:8000/api/create/', headers={'Authorization': 'Bearer '+request.session['token'] }, data={'name' : name,'is_directory':True, 'path':path}).json()
            if('error' in r):
                return HttpResponseRedirect('?path='+path+"&error="+r['error'])
        # 파일 업로드 부분
        elif('filedata' in request.FILES):
            file = request.FILES['filedata']
            files = {'upload_file':file}
            r = requests.post('http://127.0.0.1:8000/api/upload/',
                              headers={'Authorization': 'Bearer ' + request.session['token']},
                              data={'name': file.name, 'is_directory': False, 'path': path}, files=files).json()
            print("UPLOADED:::::", r)
            if ('error' in r):
                return HttpResponseRedirect('?error=' + r['error'])
        if(path!='/'):
            return redirect('list-view',path[1:])
        else:
            return redirect('list-view')

def DeleteView(request, path):
    path = '/'+path
    if(not check_auth(request)):
        return redirect('user-login')
    if(request.method=='GET'):
        r = requests.post('http://127.0.0.1:8000/api/delete/', headers={'Authorization': 'Bearer '+request.session['token'] }, data={'path':path}).json()
        if('error' in r):
            return redirect('list-view')
        parentpath = path[1:path.rfind('/')]
        if(parentpath!=''):
            return redirect('list-view',path[1:path.rfind('/')])
        else:
            return redirect('list-view')

def DownloadView(request, path):
    path='/'+path
    if(not check_auth(request)):
        return redirect('user-login')
    if(request.method == 'GET'):
        error=''
        if 'error' in request.GET:
            error = request.GET['error']
        r = requests.get('http://127.0.0.1:8000/api/download'+path, headers={'Authorization': 'Bearer '+ request.session['token'] }).json()
        print("DOWNLOADED",r)
        if('error' in r):
            return redirect('list-view')
        file = open(r['url'], 'rb')
        data = file.read()
        file.close()
        response = HttpResponse(data, content_type=r['type'])
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % urllib.parse.quote(r['name'].encode('utf-8'))
        print("DOWNLOADED",r)
        return response

def LogoutView(request):
    del request.session['token']
    return redirect('user-login')