from django.shortcuts import render
from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.views import APIView, Response
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


def reduce_parent_size(parent, size):
    with transaction.atomic():
        tmp = parent
        while(not tmp == None):
            obj = File.objects.select_for_update().get(id=tmp.id)
            obj.size = obj.size - int(size)
            obj.save()
            tmp = tmp.parent


def increase_parent_size(parent, size):
    with transaction.atomic():
        tmp = parent
        while(not tmp == None):
            obj = File.objects.select_for_update().get(id=tmp.id)
            obj.size = obj.size + int(size)
            obj.save()
            tmp = tmp.parent

def reduce_user_size(user, size):
    with transaction.atomic():
        obj = User.objects.select_for_update().get(email=user.email)
        obj.cur_size = obj.cur_size - int(size)
        obj.save()

def increase_user_size(user, size):
    with transaction.atomic():
        obj = User.objects.select_for_update().get(email=user.email)
        obj.cur_size = obj.cur_size + int(size)
        obj.save()


def copy_files(user, object, parent, origin_name, to_path, from_path):
    for file in File.objects.filter(parent=object):
        origin_path = file.path
        copied_path = to_path + origin_name + "/" + origin_path[origin_path.find(from_path)+len(from_path):]
        copy_object(str(user.id), origin_path, copied_path)
        new_object = {'name': file.name, 'is_directory': file.is_directory, 'path':copied_path}
        serializer = FileSerializer(data=new_object)
        if (serializer.is_valid()):
            serializer.save(owner=user, parent=parent, is_directory=file.is_directory,
                            size=file.size, path=copied_path)
            if(not file.is_directory):
                increase_user_size(user, file.size)
        if(file.is_directory):
            new_object = File.objects.get(owner=user, parent=parent, is_directory=file.is_directory, size=file.size, path=copied_path)
            copy_files(user, file, new_object, origin_name, to_path, from_path)


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
            try:
                reduce_parent_size(directory, test[0].size)
                reduce_user_size(request.user, test[0].size)
            except:
                return Response({"status": "400", "error": "An error occured"}, status=status.HTTP_400_BAD_REQUEST)

            test[0].size = size
            test[0].modified = timezone.now()
            test[0].save()

            try:
                increase_parent_size(directory, test[0].size)
                increase_user_size(request.user, test[0].size)
            except:
                return Response({"status": "400", "error": "An error occured"}, status=status.HTTP_400_BAD_REQUEST)

            complete_multipart_upload(str(request.user.id), filepath, UploadId, MultipartUpload)
            serializer = FileSerializer(test[0])
            result['item'] = serializer.data
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            serializer = FileSerializer(data=request.data)
            if(serializer.is_valid()):
                serializer.save(owner=request.user, parent=directory, is_directory=False, size=size, path=filepath)
                try:
                    increase_parent_size(directory, size)
                    increase_user_size(request.user, size)
                except:
                    return Response({"status": "400", "error": "An error occured"}, status=status.HTTP_400_BAD_REQUEST)

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
                reduce_user_size(request.user, object.size)
                reduce_parent_size(object.parent, object.size)
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
            to_parent_object = File.objects.get(owner=request.user, path=request.data['to_path'])
            tmp = to_parent_object
            origin_name = from_object.name
            while(not tmp == None):
                if(tmp == from_object):
                    return Response({"status": "400", "error": "Cannot copy"}, status=status.HTTP_400_BAD_REQUEST)
                tmp = tmp.parent

            found = False
            name = origin_name
            i = 1
            while(not found):
                if(from_object.is_directory):
                    duplicated = File.objects.filter(owner=request.user, path=request.data['to_path'] + name + "/")
                else:
                    duplicated = File.objects.filter(owner=request.user, path=request.data['to_path'] + name)
                if (len(duplicated) > 0):
                    name = origin_name + " ("+str(i)+")"
                    i += 1
                else:
                    found = True

            increase_parent_size(to_parent_object, from_object.size)
            if(from_object.is_directory):
                copy_object(str(request.user.id), request.data['from_path'], request.data['to_path'] + name + "/")
                new_object = {'name': name, 'is_directory': from_object.is_directory, 'path': request.data['to_path'] + name + "/"}
            else:
                copy_object(str(request.user.id), request.data['from_path'], request.data['to_path'] + name)
                new_object = {'name': name, 'is_directory': from_object.is_directory, 'path': request.data['to_path'] + name}
            serializer = FileSerializer(data=new_object)

            if (serializer.is_valid()):
                if (from_object.is_directory):
                    serializer.save(owner=request.user, parent=to_parent_object, is_directory=from_object.is_directory,
                                    size=from_object.size, path=request.data['to_path'] + name + "/")
                    new_object = File.objects.get(owner=request.user, parent=to_parent_object, is_directory=from_object.is_directory,
                                    size=from_object.size, path=request.data['to_path'] + name + "/")
                    copy_files(request.user, from_object, new_object, name, request.data['to_path'],
                               from_object.path)
                else:
                    serializer.save(owner=request.user, parent=to_parent_object, is_directory=from_object.is_directory,
                                    size=from_object.size, path=request.data['to_path'] + name)
                    increase_user_size(request.user, from_object.size)

                return Response(serializer.data, status=status.HTTP_200_OK)

        except File.DoesNotExist:
            return Response({"status": "404", "error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"status": "400", "error": "An error occured"}, status=status.HTTP_400_BAD_REQUEST)

class FileMoveApi(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:

            from_object = File.objects.get(owner=request.user, path=request.data['from_path'])
            to_parent_object = File.objects.get(owner=request.user, path=request.data['to_path'])
            origin_name = from_object.name
            tmp = to_parent_object
            while(not tmp == None):
                if(tmp == from_object):
                    return Response({"status": "400", "error": "Cannot move"}, status=status.HTTP_400_BAD_REQUEST)
                tmp = tmp.parent

            found = False
            name = origin_name
            i = 1
            while(not found):
                if(from_object.is_directory):
                    duplicated = File.objects.filter(owner=request.user, path=request.data['to_path'] + name + "/")
                else:
                    duplicated = File.objects.filter(owner=request.user, path=request.data['to_path'] + name)
                if (len(duplicated) > 0):
                    name = origin_name + " ("+str(i)+")"
                    i += 1
                else:
                    found = True

            if(from_object.is_directory):
                childrens = from_object.get_all_children()
                for child in childrens:
                    if(child != from_object):
                        origin_path = child.path
                        moved_path = request.data['to_path'] + name + "/" + origin_path[origin_path.find(from_object.path) + len(from_object.path):]
                        child.path = moved_path
                        child.save()
                        move_object(str(request.user.id), origin_path, moved_path)

            reduce_parent_size(from_object.parent, from_object.size)
            increase_parent_size(to_parent_object, from_object.size)
            if(from_object.is_directory):
                from_object.path = request.data['to_path'] + name + "/"
            else:
                from_object.path = request.data['to_path'] + name
            from_object.name = name
            from_object.parent = to_parent_object
            from_object.save()
            if(from_object.is_directory):
                move_object(str(request.user.id), request.data['from_path'], request.data['to_path'] + name + "/")
            else:
                move_object(str(request.user.id), request.data['from_path'], request.data['to_path'] + name )
            serializer = FileSerializer(from_object)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except File.DoesNotExist:
            return Response({"status": "404", "error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

        except:
            return Response({"status": "400", "error": "An error occured"}, status=status.HTTP_400_BAD_REQUEST)


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
            if(user == request.user):
                return Response({"status": "400", "error": "Cannot share to owner"}, status=status.HTTP_400_BAD_REQUEST)
            shared = Share.objects.filter(owner=user, file=object)
            if(len(shared)>0):
                return Response({"status": "400", "error": "Already Shared"}, status=status.HTTP_400_BAD_REQUEST)

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


class ListDoShareApi(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        result = {}
        items = []
        result['parent'] = ''
        files = File.objects.filter(owner=request.user, share__in=Share.objects.all())
        shares = Share.objects.all()
        for share in shares:
            try:
                file = File.objects.get(owner=request.user, id=share.file.id)
                item = FileSerializer(file)
                data = item.data
                data['shared_id'] = share.id
                data['shared_user'] = share.owner.username
                items.append(data)
            except File.DoesNotExist:
                pass



        result['available_size'] = request.user.max_size - request.user.cur_size
        result['used_size'] = request.user.cur_size
        result['offset'] = 0
        result['username'] = request.user.username
        result['length'] = len(items)
        result['items'] = items

        return Response(result, status=status.HTTP_200_OK)


class ShareDeleteApi(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            object = Share.objects.get(id=request.data.get('id',''))

            serializer = ShareSerializer(object)
            object.delete()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except File.DoesNotExist:
            return Response({"status": "404", "error": "File Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except Share.DoesNotExist:
            return Response({"status": "404", "error": "This File is not Shared"}, status=status.HTTP_404_NOT_FOUND)