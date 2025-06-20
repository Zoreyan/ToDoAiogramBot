from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


urlpatterns = [
    path('categories/', CategoryListView.as_view()),
    path('categories/create/', CategoryCreateView.as_view()),
    path('categories/<int:pk>/', CategoryDetailView.as_view()),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view()),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view()),
    path('tasks/', TaskListView.as_view()),
    path('tasks/create/', TaskCreateView.as_view()),
    path('tasks/<int:pk>/', TaskDetailView.as_view()),
    path('tasks/<int:pk>/update/', TaskUpdateView.as_view()),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view()),
    path('tasks/<int:pk>/complete/', TaskCompleteView.as_view()),
    path('authenticate/', AuthenticateUser.as_view())
]