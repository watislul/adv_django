from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import User, Project, Category, Priority, Task
from .permissions import IsEmployee, IsManager, IsAdmin
from .serializers import (
    UserSerializer,
    ProjectSerializer,
    CategorySerializer,
    PrioritySerializer,
    TaskSerializer,
)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsManager]


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PriorityViewSet(ModelViewSet):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsEmployee]


def index(request):
    return render(request, "core/index.html")
