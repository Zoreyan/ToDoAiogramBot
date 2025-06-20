from rest_framework import viewsets, views, status
from .models import Category, Task, User
from .serializers import CategorySerializer, TaskSerializer
from rest_framework.response import Response
from datetime import timedelta, datetime
from django.utils import timezone
from .tasks import send_telegram_notification




class CategoryListView(views.APIView):
    def get(self, request, *args, **kwargs):
        try:
            telegram_id = request.data.get('telegram_id')
            categories = Category.objects.filter(user__telegram_id=telegram_id)
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class CategoryCreateView(views.APIView):
    def post(self, request, *args, **kwargs):
        try:

            telegram_id = request.data.get('telegram_id')
            title = request.data.get('title')
            if not telegram_id or not title:
                return Response({"error": "telegram_id and title are required"}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(telegram_id=telegram_id)
            Category.objects.create(user=user, title=title)
            return Response({"success": "Category successfully created"}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class CategoryDetailView(views.APIView):
    def get(self, request, pk, *args, **kwargs):
        try:
            category = Category.objects.get(id=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)


class CategoryUpdateView(views.APIView):
    def put(self, request, pk, *args, **kwargs):
        try:
            category = Category.objects.get(pk=pk, user=request.user)
            serializer = CategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        

class CategoryDeleteView(views.APIView):
    def delete(self, request, pk, *args, **kwargs):
        try:
            category = Category.objects.get(id=pk)
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)



class TaskListView(views.APIView):
    def get(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        tasks = Task.objects.filter(user__telegram_id=telegram_id)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    

class TaskCreateView(views.APIView):
    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        title = request.data.get('title')
        due_date_str = request.data.get('due_date')
        category_id = request.data.get('category_id')

        if not telegram_id or not title:
            return Response({"error": "telegram_id and title are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id, user=user)
            except Category.DoesNotExist:
                return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        due_date = None
        try:
            due_date = timezone.make_aware(datetime.fromisoformat(due_date_str))
        except ValueError:
            return Response({"error": "Invalid due_date format. Use YYYY-MM-DD HH:MM"}, status=status.HTTP_400_BAD_REQUEST)

        task = Task.objects.create(
            user=user,
            title=title,
            due_date=due_date,
            category=category
        )

        if due_date:
            # Отправляем уведомление за 2 часа до срока выполнения задачи
            if due_date < timezone.now():
                return Response({"error": "Due date must be in the future"}, status=status.HTTP_400_BAD_REQUEST)
        # Здесь указываем сколько времени до отправки уведомления
        send_time = due_date - timedelta(minutes=120)
        send_telegram_notification.apply_async(
            args=[telegram_id, f"⏰ Напоминание: {title} скоро истекает!"],
            eta=send_time
        )

        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskDetailView(views.APIView):
    def get(self, request, pk, *args, **kwargs):
        try:
            telegram_id = request.data.get('telegram_id')
            task_id = request.data.get('task_id')
            print(telegram_id, task_id)
            if not telegram_id:
                return Response({"error": "telegram_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(telegram_id=telegram_id)
            task = Task.objects.get(id=task_id, user=user)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        

class TaskUpdateView(views.APIView):
    def put(self, request, pk, *args, **kwargs):
        try:
            task = Task.objects.get(pk=pk, user=request.user)
            serializer = TaskSerializer(task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        
class TaskDeleteView(views.APIView):
    def delete(self, request, pk, *args, **kwargs):
        try:
            task = Task.objects.get(id=pk)
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


class TaskCompleteView(views.APIView):
    def post(self, request, pk, *args, **kwargs):
        try:
            task = Task.objects.get(id=pk)
            task.is_completed = True
            task.save()
            return Response({"message": "Task marked as completed"}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


class AuthenticateUser(views.APIView):
    """
    Аутентификация пользователя по Telegram ID.
    Если пользователь с таким ID не существует, он будет создан.
    """

    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')

        if not telegram_id:
            return Response({"error": "telegram_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={"username": f"tg_{telegram_id}"}
        )

        if created:
            user.set_unusable_password()
            user.save()

        return Response({
            "message": "user created" if created else "user exists",
            "user_id": user.id
        })
    
