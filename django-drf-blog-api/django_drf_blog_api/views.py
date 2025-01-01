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

class PostView(APIView):  # Authors
    permission_classes = [IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        posts = Post.objects.filter(user=self.request.user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        post_id = request.data.get('id')

        try:
            post = Post.objects.get(
                id=post_id, user=self.request.user)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=404)

        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        content = request.data.get('content')
        category = request.data.get('category')
        tags = request.data.get('tags')
        keywords = request.data.get('keywords')

        if not title or not content or not category:
            return Response({'error': 'Title, Content and Category are required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.create(
                user=request.user, title=title, content=content, category=category, tags=tags, keywords=keywords)

            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        post_id = request.data.get('id')
        try:
            post = Post.objects.get(id=post_id)
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
