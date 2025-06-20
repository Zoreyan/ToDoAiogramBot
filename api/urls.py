from django.urls import path
from .views import *


urlpatterns = [
    path('categories/', CategoryListView.as_view()),
    path('categories/create/', CategoryCreateView.as_view()),
    path('categories/<str:pk>/', CategoryDetailView.as_view()),
    path('categories/<str:pk>/update/', CategoryUpdateView.as_view()),
    path('categories/<str:pk>/delete/', CategoryDeleteView.as_view()),
    path('tasks/', TaskListView.as_view()),
    path('tasks/create/', TaskCreateView.as_view()),
    path('tasks/<str:pk>/', TaskDetailView.as_view()),
    path('tasks/<str:pk>/update/', TaskUpdateView.as_view()),
    path('tasks/<str:pk>/delete/', TaskDeleteView.as_view()),
    path('tasks/<str:pk>/complete/', TaskCompleteView.as_view()),
    path('authenticate/', AuthenticateUser.as_view())
]