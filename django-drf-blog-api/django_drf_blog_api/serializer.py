from rest_framework import serializers
from .models import *
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model

user = get_user_model()


from media_library.serializers import MediaAssetSerializer
from media_library.models import MediaAsset


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


class AuthorSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)

    class Meta:
        model = Author
        fields = ('id', 'user', 'role', 'bio')


class MagazineSeriesSerializer(serializers.ModelSerializer):
    cover_media = MediaAssetSerializer(read_only=True)
    cover_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), source='cover_media', write_only=True, required=False, allow_null=True
    )
    cover_image = serializers.ReadOnlyField()

    class Meta:
        model = MagazineSeries
        fields = (
            'id',
            'series_number',
            'edition_code',
            'date',
            'title',
            'subtitle',
            'badge',
            'cover_media',
            'cover_media_id',
            'cover_image_url',
            'cover_image',
            'editorial_summary',
            'lead_stories',
            'slug',
            'created_at',
            'updated_at'
        )


class PostSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    keywords = KeywordSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    magazine_series = MagazineSeriesSerializer(read_only=True)
    magazine_series_id = serializers.PrimaryKeyRelatedField(
        queryset=MagazineSeries.objects.all(), source='magazine_series', write_only=True, required=False, allow_null=True
    )
    featured_media = MediaAssetSerializer(read_only=True)
    featured_media_id = serializers.PrimaryKeyRelatedField(
        queryset=MediaAsset.objects.all(), source='featured_media', write_only=True, required=False, allow_null=True
    )
    featured_image = serializers.ReadOnlyField()
    readTime = serializers.IntegerField(source='read_time', read_only=True)
    total_comments = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'content',
            'excerpt',
            'read_time',
            'readTime',
            'pub_date',
            'updated_at',
            'slug',
            'category',
            'tags',
            'keywords',
            'author',
            'magazine_series',
            'magazine_series_id',
            'featured_media',
            'featured_media_id',
            'featured_image_url',
            'featured_image_url_caption',
            'featured_image',
            'total_comments',
            'total_likes',
            'safe_post_content_html')

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
