from rest_framework import serializers
from .models import *
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model

user = get_user_model()


# class UserCreateSerializer(UserCreateSerializer):
#     class Meta(UserCreateSerializer.Meta):
#         model = user
#         fields = ('id', 'first_name', 'last_name',
#                   'phone_number', 'email', 'password')


class UserInfoSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = user
        fields = ('id', 'first_name', 'last_name',
                  'phone_number', 'email', 'get_image_url', 'get_photo_url', 'profile_picture')


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
        return CommentSerializer(replies, many=True, context=self.context).data


class PostSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    tags = TagSerializer(many=True)
    keywords = KeywordSerializer(many=True)
    author = UserInfoSerializer()
    total_comments = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'pub_date', 'slug', 'category',
                  'tags', 'keywords', 'author', 'image', 'image_caption', 'total_comments', 'total_likes')

    def get_total_comments(self, obj):
        # Count the comments related to the post
        return Comment.objects.filter(post=obj).count()

    def get_total_likes(self, obj):
        # Count the likes for the post
        content_type = ContentType.objects.get_for_model(Post)
        return Like.objects.filter(content_type=content_type, object_id=obj.id).count()


class LikeSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer()
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Like
        fields = ('id', 'user', 'content_object', 'created_at')

    def get_content_object(self, obj):
        return str(obj.content_object)
