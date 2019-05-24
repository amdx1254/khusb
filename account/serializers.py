from rest_framework import serializers
from .models import User
from django.core.validators import validate_email
from file.models import File
import os
from django.conf import settings
# 회원 정보 Serializer
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('userid', 'username', 'email', 'password')
        extra_kwargs = {
            'password' : {'write_only' : True }
        }

    def validate(self, attrs):
        email = attrs['email']
        user = User.objects.filter(email=email)
        if(user.exists()):
            raise serializers.ValidationError("Email is already in use")

        if(validate_email(email)):
            raise serializers.ValidationError("Email is not correct")
        return attrs

    def create(self, validated_data):
        username = validated_data['username']
        userid = validated_data['userid']
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(userid=userid, email=email, password=password, username=username)
        folder = File.objects.create(parent=None, owner=user, name='/', is_directory=True, path='/')
        if not os.path.exists(settings.MEDIA_ROOT + "_" + user.userid):
            os.mkdir(settings.MEDIA_ROOT + "_" + user.userid)
        user.save()
        return validated_data