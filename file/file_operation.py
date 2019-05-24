import os
from django.conf import settings
import shutil


def create_directory(user, path):
    if not os.path.exists(settings.MEDIA_ROOT+"_"+user):
        os.mkdir(settings.MEDIA_ROOT+"_"+user)
    os.mkdir(settings.MEDIA_ROOT+"_"+user+"/"+path)
    print("GOOD")


def create_file(user,path,file, filename):
    fp = open(settings.MEDIA_ROOT+"_"+user+"/"+path+"/"+filename, 'wb')
    for chunk in file.chunks():
        fp.write(chunk)
    fp.close()


def download_file(user, path, filename):
    """
    file = open(settings.MEDIA_ROOT + "_" + user + "/" + path, 'rb')
    data = file.read()
    file.close()
    """
    #shutil.copyfile(settings.MEDIA_ROOT + "_" + user + path,  settings.MEDIA_ROOT)
    return settings.MEDIA_ROOT+"_"+user+path
    #return data

def delete_file(user,path, is_directory):
    if(not is_directory):
        os.remove(settings.MEDIA_ROOT+"_"+user+"/"+path)
    else:
        shutil.rmtree(settings.MEDIA_ROOT+"_"+user+"/"+path)