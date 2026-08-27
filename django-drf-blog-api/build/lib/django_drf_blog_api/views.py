from django.shortcuts import render
from rest_framework import generics
from .models import *
from .serializer import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from djoser.views import UserViewSet
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.contenttypes.models import ContentType


class PostListView(generics.ListAPIView):  # Public users
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [AllowAny,]


class PostDetailView(generics.RetrieveAPIView):
    lookup_field = 'slug'
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny,]


class CategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny,]

class TagView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny,]

from media_library.models import MediaAsset


class MagazineSeriesListView(generics.ListAPIView):  # Public
    queryset = MagazineSeries.objects.all()
    serializer_class = MagazineSeriesSerializer
    permission_classes = [AllowAny]


class MagazineSeriesDetailView(generics.RetrieveAPIView):  # Public
    lookup_field = 'slug'
    queryset = MagazineSeries.objects.all()
    serializer_class = MagazineSeriesSerializer
    permission_classes = [AllowAny]


class PostView(APIView):  # Authors
    permission_classes = [IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        author_profile, _ = Author.objects.get_or_create(user=self.request.user)
        posts = Post.objects.filter(author=author_profile)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        post_id = request.data.get('id')
        author_profile, _ = Author.objects.get_or_create(user=self.request.user)

        try:
            post = Post.objects.get(
                id=post_id, author=author_profile)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=404)

        title = request.data.get('title', post.title)
        content = request.data.get('content', post.content)
        excerpt = request.data.get('excerpt', post.excerpt)
        read_time = request.data.get('read_time') or request.data.get('readTime') or post.read_time
        featured_media_id = request.data.get('featured_media_id') or request.data.get('featured_media')
        featured_image_url = request.data.get('featured_image_url') or request.data.get('featured_image')
        featured_image_url_caption = request.data.get('featured_image_url_caption', post.featured_image_url_caption)
        magazine_series_id = request.data.get('magazine_series_id') or request.data.get('magazine_series')

        if magazine_series_id:
            try:
                post.magazine_series = MagazineSeries.objects.get(id=magazine_series_id)
            except MagazineSeries.DoesNotExist:
                pass

        if featured_media_id:
            try:
                post.featured_media = MediaAsset.objects.get(id=featured_media_id)
            except MediaAsset.DoesNotExist:
                pass
        elif featured_image_url:
            post.featured_image_url = featured_image_url
            post.featured_media = None

        post.title = title
        post.content = content
        post.excerpt = excerpt
        post.read_time = read_time
        post.featured_image_url_caption = featured_image_url_caption
        post.save()

        serializer = PostSerializer(post)
        return Response(serializer.data, status=200)

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        content = request.data.get('content')
        category_id = request.data.get('category')
        excerpt = request.data.get('excerpt', '')
        read_time = request.data.get('read_time') or request.data.get('readTime') or 0
        featured_media_id = request.data.get('featured_media_id') or request.data.get('featured_media')
        featured_image_url = request.data.get('featured_image_url') or request.data.get('featured_image')
        featured_image_url_caption = request.data.get('featured_image_url_caption', '')
        magazine_series_id = request.data.get('magazine_series_id') or request.data.get('magazine_series')

        if not title or not content or not category_id:
            return Response({'error': 'Title, Content and Category are required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id) if isinstance(category_id, int) else Category.objects.get(name=category_id)
            author_profile, _ = Author.objects.get_or_create(user=request.user)

            featured_media = None
            if featured_media_id:
                try:
                    featured_media = MediaAsset.objects.get(id=featured_media_id)
                except MediaAsset.DoesNotExist:
                    pass

            magazine_series = None
            if magazine_series_id:
                try:
                    magazine_series = MagazineSeries.objects.get(id=magazine_series_id)
                except MagazineSeries.DoesNotExist:
                    pass

            post = Post.objects.create(
                author=author_profile, title=title, content=content, category=category,
                excerpt=excerpt, read_time=read_time, featured_media=featured_media,
                featured_image_url=featured_image_url if not featured_media else None,
                featured_image_url_caption=featured_image_url_caption,
                magazine_series=magazine_series)

            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        post_id = request.data.get('id')
        author_profile, _ = Author.objects.get_or_create(user=self.request.user)
        try:
            post = Post.objects.get(id=post_id, author=author_profile)
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


class CommentListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Get the post_id from query parameters
        post_id = request.GET.get('post_id')
        if not post_id:
            return Response({"error": "Missing 'post_id' query parameter."}, status=400)

        # Validate if the post exists
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=404)

        # Fetch comments for the post
        comments = Comment.objects.filter(post=post, parent=None)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentView(APIView):
    permission_classes = [IsAuthenticated,]

    def put(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        comment = request.data.get('comment')
        post_id = request.data.get('post')
        parent_comment_id = request.data.get('parent_comment')

        if not comment or not post_id:
            return Response({'error': 'Comment and Post_ID are required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=post_id)

            if parent_comment_id:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                comment = Comment.objects.create(
                    user=request.user, comment=comment, post=post, parent=parent_comment)
            else:
                comment = Comment.objects.create(
                    user=request.user, comment=comment, post=post)

            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        pass


class LikeView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        content_type = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')

        if not content_type or not object_id:
            return Response({'error': 'content_type and object_id are required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content_type = ContentType.objects.get(model=content_type)
        except ContentType.DoesNotExist:
            return Response({'error': 'Invalid content_type.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has liked the object
        liked = Like.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        ).exists()

        return Response({'liked': liked}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        content_type = request.data.get('content_type')
        object_id = request.data.get('object_id')

        if not content_type or not object_id:
            return Response({'error': 'content_type and object_id are required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content_type = ContentType.objects.get(model=content_type)
        except ContentType.DoesNotExist:
            return Response({'error': 'Invalid content_type.'}, status=status.HTTP_400_BAD_REQUEST)

        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        )

        if created:
            return Response({'message': 'Liked successfully.'}, status=status.HTTP_201_CREATED)
        else:
            like.delete()
            return Response({'message': 'Unliked successfully.'}, status=status.HTTP_200_OK)


class TotalLikesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        content_type = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')

        if not content_type or not object_id:
            return Response({'error': 'content_type and object_id are required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content_type = ContentType.objects.get(model=content_type)
        except ContentType.DoesNotExist:
            return Response({'error': 'Invalid content_type.'}, status=status.HTTP_400_BAD_REQUEST)

        total_likes = Like.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).count()

        return Response({'total_likes': total_likes}, status=status.HTTP_200_OK)
