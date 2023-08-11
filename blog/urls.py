from django.urls import path
from .views import *

urlpatterns = [
    path('categoty', CategoryView.as_view()),
]
