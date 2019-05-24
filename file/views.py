from django.shortcuts import render
from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.views import APIView, Response
from .permissions import IsOwnerOrReadOnly
from .models import File
from .serializers import FileSerializer
from rest_framework_jwt.authentication import  JSONWebTokenAuthentication
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .file_operation import *
import shutil
import os


# Create your views here.
# CreateAPIView를 통해 post를 통해 입력 받은 값을 자동으로 AccountSerializer를 통해 생성시켜줌.
class FolderCreateApi(APIView):
    permission_classes = (IsAuthenticated, )
    def post(self, request):
        try:
            path = request.data['path']
            name = request.data['name']
            directory = File.objects.get(owner=request.user,path=path)
        except File.DoesNotExist:
            return Response({"status": "404", "error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        test = File.objects.filter(owner=request.user, parent=directory, name=name, is_directory=True)

        if len(test)>0:
            return Response({"status": "400", "error": "Already Exist"}, status=status.HTTP_400_BAD_REQUEST)
        if(path=='/'):
            folderpath = path+name
        else:
            folderpath = path+'/'+name
        serializer = FileSerializer(data=request.data)
        print(serializer.is_valid())
        if(serializer.is_valid()):
            serializer.save(owner=request.user, parent=directory, is_directory=True, path=folderpath)
            print(directory.__str__()+request.data['name'])
            create_directory(str(request.user.userid), directory.__str__()+'/'+request.data['name'])
            print("AAAAAAAABBBBBBBBBBBBBBBBBBBBBbAAA",serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FolderListApi(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self, request, path='/'):
        if(path!='/'):
            path='/'+path
        try:
            print("AAAA:",path)
            directory = File.objects.get(owner=request.user, path=path)
            print(directory)
            files = File.objects.filter(parent=directory)
        except File.DoesNotExist:
            return Response({"status": "404", "error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        result = {}
        result['path'] = path
        result['items'] = []
        for file in files:
            ser = FileSerializer(file)
            result['items'].append(ser.data)

        return Response(result)

class FileCreateApi(APIView):
    permission_classes = (IsAuthenticated, )
    def post(self, request):
        filepath = ''
        try:
            name = request.data['name']
            path = request.data['path']
            if (path == '' or path=='/'):
                path = '/'
                filepath = path+name
            elif (path[-1] == '/' and path != '/'):
                path = path[:-1]
                filepath = path + '/' + name
            else:
                filepath = path + '/' + name
            directory = File.objects.get(owner=request.user, path=path)
        except File.DoesNotExist:
            return Response({"status": "404", "error": "Parent Not Found"}, status=status.HTTP_404_NOT_FOUND)
        test = File.objects.filter(owner=request.user, parent=directory, name=name, is_directory=False)
        if len(test)>0:
            return Response({"status": "400", "error": "Already Exist"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FileSerializer(data=request.data)

        if(serializer.is_valid()):
            serializer.save(owner=request.user, parent=directory, is_directory=False, size=len(request.FILES['upload_file']), path=filepath)
            print("AAAAAAA",serializer.data)
            create_file(str(request.user.userid), directory.__str__()+'/', request.FILES['upload_file'], request.data['name'])
            if (os.path.exists(settings.MEDIA_ROOT)):
                shutil.rmtree(settings.MEDIA_ROOT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FileDeleteApi(APIView):
    permission_classes = (IsAuthenticated, )
    def post(self, request):
        try:
            object = File.objects.get(owner=request.user,path=request.data['path'])

            is_root = True if object.path == '/' else False
            if (is_root):
                return Response({"status": "400", "error": "Cannot remove root directory"},
                                status=status.HTTP_400_BAD_REQUEST)
            delete_file(request.user.userid, object.__str__(), object.is_directory)
            serializer = FileSerializer(object)
            object.delete()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except File.DoesNotExist:
            return Response({"status": "404", "error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

class FileDownloadApi(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self, request, path):
        path = '/'+path
        try:
            file = File.objects.get(owner=request.user, path=path)
            path = download_file(file.owner.userid, file.__str__(), file.name)
            serializer = FileSerializer(file).data
            serializer['url'] = path
            return Response(serializer)
        except File.DoesNotExist:
            return Response({"status":"404", "error":"Not Found"})



#def Fileupload(request, path, filename,)
