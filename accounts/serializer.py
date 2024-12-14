from .models import *
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model

user = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = user
        fields = ('id', 'first_name', 'last_name',
                  'phone_number', 'email', 'password')


class UserInfoSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = user
        fields = ('id', 'first_name', 'last_name', 'phone_number', 'email', 'get_photo_url', 'date_of_birth',
                  'gender', 'home_address', 'local_govt', 'state_of_origin', 'nationality', 'image',)
