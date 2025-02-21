from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path(
        '',
        views.index,
        name='index'
    ),path(
        'register/',
        views.register,
        name='register'
    ),path(
        'login/',
        auth_views.LoginView.as_view(template_name='app/login.html'),
        name='login'
    ),path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),path(
        'add-food/',
        views.add_food,
        name='add-food'
    ),path(
        'update-goals/',
        views.update_goals,
        name='update-goals'
    ),path(
        'chart-data/',
        views.chart_data,
        name='chart-data'
    ),
]