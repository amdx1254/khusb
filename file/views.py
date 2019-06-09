from django.shortcuts import render
from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.views import APIView, Response
from .permissions import IsOwnerOrReadOnly
from account.models import User
from .models import File, Share
from .serializers import FileSerializer, ShareSerializer
from rest_framework_jwt.authentication import  JSONWebTokenAuthentication
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .file_operation import *
from .utils import *
import requests
import json
from django.utils import timezone
from django.db import transaction

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
            sort = request.GET.get('recently','')
            directory = File.objects.get(owner=request.user, path=path)
            if(sort=='modified'):
                files = File.objects.filter(owner=request.user, is_directory=False).order_by('-modified')[:10]
            elif(sort=='created'):
                files = File.objects.filter(owner=request.user, is_directory=False).order_by('-created')[:10]
            else:
                files = File.objects.filter(owner=request.user, parent=directory).order_by('name')
        except File.DoesNotExist:
            return Response({"status": "404", "error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        result = {}
        dir = FileSerializer(directory)
        result['available_size'] = request.user.max_size - request.user.cur_size
        result['used_size'] = request.user.cur_size
        result['offset'] = 0
        result['username'] = request.user.username
        if(directory.parent is not None):
            result['parent'] = str(directory.parent)
        else:
            result['parent'] = '/'
        result['path'] = path
        result['items'] = []
        for file in files:
            ser = FileSerializer(file)
            if(sort == ''):
                result['items'].append(ser.data)
            else:
                if(file.path != '/' and not file.is_directory):
                    result['items'].append(ser.data)
        print(len(result['items']))
        return Response(result, status=status.HTTP_200_OK)


class FavoriteListApi(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        files = File.objects.filter(owner=request.user, favorite=True)
        result = {}
        result['available_size'] = request.user.max_size - request.user.cur_size
        result['used_size'] = request.user.cur_size
        result['offset'] = 0
        result['username'] = request.user.username
        result['items'] = []
        for file in files:
            ser = FileSerializer(file)
            result['items'].append(ser.data)

        return Response(result, status=status.HTTP_200_OK)


class FileSearchApi(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, path='/'):
        if(path!='/'):
            path='/'+path+'/'
        try:
            directory = File.objects.get(owner=request.user, path=path)
            files = directory.get_all_children()
            print("fuck")
        except File.DoesNotExist:
            return Response({"status": "404", "error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        result = {}
        name = request.GET.get('name','')
        type = request.GET.get('type','all')
        sort = request.GET.get('sort','name')
        print(path+name)
        items = []
        for file in files:
            if(name.lower() in file.name.lower()):
                result_item = FileSerializer(file)
                items.append(result_item.data)
        result['available_size'] = request.user.max_size - request.user.cur_size
        result['used_size'] = request.user.cur_size
        result['offset'] = 0
        result['length'] = len(items)
        result['name'] = name
        result['sort'] = sort
        result['items'] = items


        return Response(result, status=status.HTTP_200_OK)


class FileCreateStartApi(APIView):
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

        """
        if len(test)>0:
            test[0].modified = datetime.datetime.now()
            test[0].save()
            return Response({"status": "400", "error": "Already Exist"}, status=status.HTTP_400_BAD_REQUEST)
        """

        serializer = FileSerializer(data={'name':name, 'path':filepath, 'size':size})
        if(serializer.is_valid()):
            uploadid = create_multipart_upload(str(request.user.id), serializer.data['path'])
            urls = get_upload_part_url(str(request.user.id), serializer.data['path'], size, uploadid,
                                       5 * 1024 * 1024 * 1024)
            result['item'] = serializer.data
            result['uploadid'] = uploadid
            result['url'] = urls

        return Response(result, status=status.HTTP_200_OK)


class FileCreateCompleteApi(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        print(request.data)
        result = {}
        try:
            name = request.data['name']
            path = request.data['path']
            size = request.data['size']
            UploadId = request.data['uploadid']
            MultipartUpload = json.loads(request.data['items'])
            MultipartUpload['Parts'] = sorted(MultipartUpload['Parts'], key=lambda k: k['PartNumber'])
            filepath = path + name
            directory = File.objects.get(owner=request.user, path=path)

        except File.DoesNotExist:
            return Response({"status": "404", "error": "Parent Not Found"}, status=status.HTTP_404_NOT_FOUND)
        test = File.objects.filter(owner=request.user, parent=directory, name=name, is_directory=False)


        if len(test)>0:
            tmp = directory
            while(not tmp == None):
                tmp.size = tmp.size-int(test[0].size)
                tmp.save()
                tmp=tmp.parent
            request.user.cur_size = request.user.cur_size - int(test[0].size)
            request.user.save()
            test[0].size = size
            test[0].modified = timezone.now()
            test[0].save()
            tmp = directory
            while(not tmp == None):
                tmp.size = tmp.size+int(test[0].size)
                tmp.save()
                tmp=tmp.parent
            request.user.cur_size = request.user.cur_size + int(test[0].size)
            request.user.save()
            complete_multipart_upload(str(request.user.id), filepath, UploadId, MultipartUpload)
            serializer = FileSerializer(test[0])
            result['item'] = serializer.data
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            serializer = FileSerializer(data=request.data)
            if(serializer.is_valid()):
                serializer.save(owner=request.user, parent=directory, is_directory=False, size=size, path=filepath)

                request.user.cur_size = request.user.cur_size+int(size)
                request.user.save()
                tmp = directory
                while(not tmp == None):
                    tmp.size = tmp.size+int(size)
                    tmp.modified = timezone.now()
                    tmp.save()
                    tmp = tmp.parent
                complete_multipart_upload(str(request.user.id), filepath, UploadId, MultipartUpload)
                result['item'] = serializer.data

                return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileCreateAbortApi(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        name = request.data['name']
        path = request.data['path']
        UploadId = request.data['uploadid']
        filepath = path + name

        abort_multipart_upload(str(request.user.id), filepath, UploadId)
        return Response({"status": "200", "message": "abort completed"}, status=status.HTTP_200_OK)


class FileDeleteApi(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            object = File.objects.get(owner=request.user,path=request.data['path'])

            is_root = True if object.path == '/' else False
            if (is_root):
                return Response({"status": "400", "error": "Cannot remove root directory"},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                with transaction.atomic():
                    user = User.objects.select_for_update().get(email=request.user.email)
                    user.cur_size = user.cur_size - int(object.size)
                    user.save()
            except:
                return Response({"status": "400", "error": "An error occured"}, status=status.HTTP_400_BAD_REQUEST)
            """
            request.user.cur_size = request.user.cur_size-int(object.size)
            request.user.save()
            tmp=object.parent
            """
            try:
                tmp = object.parent
                while(not tmp==None):

                    with transaction.atomic():
                        direc = File.objects.select_for_update().get(owner=request.user,path=tmp.path)
                        direc.size = direc.size-int(object.size)
                        direc.save()
                    """
                    tmp.size = tmp.size-int(object.size)
                    tmp.save()
                    """
                    tmp=tmp.parent
            except:
                return Response({"status": "400", "error": "An error occured"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FileSerializer(object)
            object.delete()
            delete_object(str(request.user.id), request.data['path'])
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


class FileFavoriteApi(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            object = File.objects.get(owner=request.user, path=request.data['path'])
            object.favorite = not object.favorite
            object.save()

            serializer = FileSerializer(object)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except File.DoesNotExist:
            return Response({"status": "404", "error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


class ShareApi(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            object = File.objects.get(owner=request.user, path=request.data['path'])
            user = User.objects.get(email=request.data['email'])

            serializer = ShareSerializer(data={"file": object.id, "read": True, "write": False})

            if(serializer.is_valid()):
                serializer.save(owner=user)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except File.DoesNotExist:
            return Response({"status": "404", "error": "FIle Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"status": "404", "error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListShareApi(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        id = request.GET.get("id","")
        result = {}
        items = []
        result['parent'] = ''
        if(id == ""):
            files = Share.objects.filter(owner=request.user)
            for file in files:
                item = FileSerializer(file.file)
                items.append(item.data)
        else:
            try:
                object = File.objects.get(id=id)
                if(object.is_shared(request.user)):
                    files = File.objects.filter(parent=object)
                    for file in files:
                        item = FileSerializer(file)
                        items.append(item.data)
                    if(object.parent.is_shared(request.user)):
                        result['parent']=str(object.parent.id)
                    else:
                        result['parent'] = ''

                else:
                    return Response({"status": "404", "error": "FIle Not Found"}, status=status.HTTP_404_NOT_FOUND)
            except File.DoesNotExist:
                return Response({"status": "404", "error": "FIle Not Found"}, status=status.HTTP_404_NOT_FOUND)

        result['available_size'] = request.user.max_size - request.user.cur_size
        result['used_size'] = request.user.cur_size
        result['offset'] = 0
        result['username'] = request.user.username
        result['length'] = len(items)
        result['items'] = items


        return Response(result, status=status.HTTP_200_OK)


class DownloadShareApi(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        try:
            print(request.GET.get("id",""))
            object = File.objects.get(id=request.GET.get("id",""))
            if(object.is_shared(request.user)):
                serializer = FileSerializer(object).data
                url = get_download_url(str(object.owner.id), object.path)
                serializer['url'] = url
                return Response(serializer)
            else:
                return Response({"status": "404", "error": "FIle Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except File.DoesNotExist:
            return Response({"status": "404", "error": "FIle Not Found"}, status=status.HTTP_404_NOT_FOUND)