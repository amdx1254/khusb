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
from .utils import *
import requests

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
        folderpath = path+name+'/'
        serializer = FileSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save(owner=request.user, parent=directory, is_directory=True, path=folderpath)
            url = get_upload_url(str(request.user.userid), folderpath)
            requests.put(url)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FolderListApi(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self, request, path='/'):
        if(path!='/'):
            path='/'+path+'/'
        try:
            directory = File.objects.get(owner=request.user, path=path)
            files = File.objects.filter(owner=request.user, parent=directory)
        except File.DoesNotExist:
            return Response({"status": "404", "error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        result = {}
        dir = FileSerializer(directory)
        if(directory.parent is not None):
            result['parent'] = str(directory.parent)
        else:
            result['parent'] = '/'
        result['path'] = path
        result['items'] = []
        for file in files:
            ser = FileSerializer(file)
            result['items'].append(ser.data)

        return Response(result)

class FileCreateApi(APIView):
    permission_classes = (IsAuthenticated, )
    def post(self, request):
        result = {}
        filepath = ''
        try:
            name = request.data['name']
            path = request.data['path']
            size = request.data['size']
            filepath = path+name
            directory = File.objects.get(owner=request.user, path=path)
        except File.DoesNotExist:
            return Response({"status": "404", "error": "Parent Not Found"}, status=status.HTTP_404_NOT_FOUND)
        test = File.objects.filter(owner=request.user, parent=directory, name=name, is_directory=False)
        if len(test)>0:
            return Response({"status": "400", "error": "Already Exist"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FileSerializer(data=request.data)

        if(serializer.is_valid()):
            serializer.save(owner=request.user, parent=directory, is_directory=False, size=size, path=filepath)
            url = get_upload_url(str(request.user.userid), serializer.data['path'])
            result['item'] = serializer.data
            result['url'] = url
            return Response(result, status=status.HTTP_201_CREATED)
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
            delete_object(str(request.user.userid), request.data['path'])
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
            serializer = FileSerializer(file).data
            url = get_download_url(str(request.user.userid),path)
            serializer['url'] = url
            return Response(serializer)
        except File.DoesNotExist:
            return Response({"status":"404", "error":"Not Found"})