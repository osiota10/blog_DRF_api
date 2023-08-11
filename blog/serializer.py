from rest_framework import serializers
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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'comment', 'created_at')


class PostSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    comments = CommentSerializer()
    tags = TagSerializer(many=True)
    Keywords = KeywordSerializer(many=True)
    author = UserInfoSerializer()

    class Meta:
        model = Post
        fields = ('id', 'content', 'pub_date', 'slug',
                  'category', 'tags', 'keywords', 'comments', 'author')
