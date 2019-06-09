from rest_framework import serializers
from .models import File, Share


class FileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username', required=False)

    class Meta:
        model = File
        fields = ('id', 'owner', 'parent', 'name', 'size', 'is_directory', 'type', 'path', 'created', 'modified', 'favorite')

    def get_type(self, obj):
        return obj.set_type()

    def create(self, validated_data):
        owner = validated_data['owner']
        parent = validated_data['parent']
        name = validated_data['name']
        is_directory = validated_data['is_directory']
        path = validated_data['path']
        if('size' in validated_data):
            size = validated_data['size']
            file = File.objects.create(owner=owner, parent=parent, name=name, is_directory=is_directory, path=path, size=size)
        else:
            file = File.objects.create(owner=owner, parent=parent, name=name, is_directory=is_directory, path=path)
        if(not is_directory):
            file.set_type()
        file.save()
        return validated_data
    

class ShareSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username', required=False)

    class Meta:
        model = Share
        fields = ('id', 'owner', 'file', 'read', 'write')

    def create(self, validated_data):
        owner = validated_data['owner']
        file = validated_data['file']
        read = validated_data['read']
        write = validated_data['write']
        share = Share.objects.create(owner=owner, file=file, read=read, write=write)
        share.save()
        return validated_data