from django.urls import path
from .views import *

urlpatterns = [
    # Public APIs
    path('category', CategoryView.as_view()),
    path('post-list', PostListView.as_view()),  
    path('post-list/<slug:slug>', PostDetailView.as_view()),  
    path('comment-list', CommentListView.as_view()),
    # Authorized users Only
    path('post', PostView.as_view()),  # Authors
    path('comment', CommentView.as_view()),
    path('like', LikeView.as_view()),
]
