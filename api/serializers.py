from rest_framework import serializers
from .models import Task, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M")
    due_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M")
    category = serializers.StringRelatedField(
        default=None, allow_null=True, read_only=True
    )
    class Meta:
        model = Task
        fields = '__all__'