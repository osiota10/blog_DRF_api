from rest_framework import serializers
from .models import *
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
    user = UserInfoSerializer()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'comment', 'created_at', 'replies')

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True).data


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


class LikeSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer()
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Like
        fields = ('id', 'user', 'content_object', 'created_at')

    def get_content_object(self, obj):
        return str(obj.content_object)
