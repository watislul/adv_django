from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('edit/<int:id>/', views.edit, name='edit'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('group_expense_list/', views.group_expense_list, name='group_expense_list'),
    path('add_group_expense/', views.add_group_expense, name='add_group_expense'),
    path('category_list/', views.category_list, name="category_list"),

]