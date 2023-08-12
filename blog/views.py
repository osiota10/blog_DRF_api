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


class CategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny,]


class PostView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        posts = Post.objects.filter(user=self.request.user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        pass

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
        pass
