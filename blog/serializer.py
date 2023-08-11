from rest_framework import serializers
from .models import *
# from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model

user = get_user_model()


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
    class Meta:
        model = Comment
        fields = ('id', 'comment', 'created_at')


class PostSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    tags = TagSerializer(many=True)
    Keywords = KeywordSerializer(many=True)

    class Meta:
        model = Post
        fields = ('id', 'content', 'pub_date', 'slug',
                  'category', 'tags', 'keywords')
