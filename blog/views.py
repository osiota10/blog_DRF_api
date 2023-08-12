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


class CommentView(APIView):
    permission_classes = [AllowAny,]

    def get(self, request, *args, **kwargs):
        # Get the post_id from query parameters
        post_id = request.GET.get('post_id')
        if post_id is None:
            return Response({"error": "Missing 'post_id' query parameter."}, status=400)

        comments = Comment.objects.filter(post_id=post_id)
        serializer = PostSerializer(comments, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        comment = request.data.get('comment')
        # Please remember to review logic again (next line)
        post_id = request.data.get('post')
        post = Post.objects.get(id=post_id)

        if not comment or not post:
            return Response({'error': 'Comment and Post are required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            comment = Post.objects.create(
                user=request.user, comment=comment, post=post)

            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        pass
