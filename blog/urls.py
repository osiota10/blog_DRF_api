from django.urls import path
from .views import *

urlpatterns = [
    path('category', CategoryView.as_view()),
    path('post-list', PostListView.as_view()),  # Public users
    path('post', PostView.as_view()),  # Authors
]
