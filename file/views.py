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
            serializer.save(owner=request.user, parent=directory, is_directory=True, path=folderpath, size=0)
            url = get_upload_url(str(request.user.id), folderpath)
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
        result['available_size'] = request.user.max_size - request.user.cur_size
        result['used_size'] = request.user.cur_size
        result['offset'] = 0
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
        try:
            name = request.data['name']
            path = request.data['path']
            size = request.data['size']
            filepath = path + name
            directory = File.objects.get(owner=request.user, path=path)

        except File.DoesNotExist:
            return Response({"status": "404", "error": "Parent Not Found"}, status=status.HTTP_404_NOT_FOUND)
        test = File.objects.filter(owner=request.user, parent=directory, name=name, is_directory=False)
        if len(test)>0:
            return Response({"status": "400", "error": "Already Exist"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FileSerializer(data=request.data)

        if(serializer.is_valid()):
            serializer.save(owner=request.user, parent=directory, is_directory=False, size=size, path=filepath)

            request.user.cur_size = request.user.cur_size+int(size)
            request.user.save()
            tmp = directory
            while(not tmp == None):
                tmp.size = tmp.size+int(size)
                tmp.save()
                tmp=tmp.parent

            url = get_upload_url(str(request.user.id), serializer.data['path'])
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
            delete_object(str(request.user.id), request.data['path'])
            request.user.cur_size = request.user.cur_size-int(object.size)
            request.user.save()
            tmp=object.parent

            while(not tmp==None):
                tmp.size = tmp.size-int(object.size)
                tmp.save()
                tmp=tmp.parent

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
            url = get_download_url(str(request.user.id),path)
            serializer['url'] = url
            return Response(serializer)
        except File.DoesNotExist:
            return Response({"status":"404", "error":"Not Found"})


class FileCopyApi(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            from_object = File.objects.get(owner=request.user, path=request.data['from_path'])
            to_parent_path = requests.data['to_path'][:requests.data['to_path'].rfind('/')+1]
            to_parent_object = File.objects.get(owner=request.user, path=to_parent_path)
            if(object.IsDirectory == True):
                return Response({"status": "400", "error": "Cannot copy directory"},
                                status=status.HTTP_400_BAD_REQUEST)
            copy_object(str(request.user.id), request.data['from_path'], request.data['to_path'])
            new_object = {'name': from_object.name, 'is_directory': from_object.is_directory, 'path': request.data['to_path']}
            serializer = FileSerializer(new_object)

            if (serializer.is_valid()):
                serializer.save(owner=request.user, parent=to_parent_object, is_directory=False, size=from_object.size, path=request.data['to_path'])
                request.user.cur_size = request.user.cur_size + from_object.size
                request.user.save()
                to_parent_object.size = to_parent_object.size + from_object.size
                to_parent_object.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

        except File.DoesNotExist:
            return Response({"status": "404", "error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class FileMoveApi(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            from_object = File.objects.get(owner=request.user, path=request.data['from_path'])
            to_parent_path = requests.data['to_path'][:requests.data['to_path'].rfind('/')+1]
            to_parent_object = File.objects.get(owner=request.user, path=to_parent_path)
            if(object.IsDirectory == True):
                return Response({"status": "400", "error": "Cannot move directory"},
                                status=status.HTTP_400_BAD_REQUEST)
            from_object.parent.size = from_object.parent.size-from_object.size
            from_object.path = requests.data['to_path']
            from_object.parent = to_parent_object
            to_parent_object.size = to_parent_object.size+from_object.size
            from_object.save()
            to_parent_object.save()
            move_object(str(request.user.id), request.data['from_path'], request.data['to_path'])
            serializer = FileSerializer(from_object)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except File.DoesNotExist:
            return Response({"status": "404", "error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
