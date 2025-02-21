from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Food, HealthGoal
from .forms import FoodForm, HealthGoalForm
from .models import Food, HealthGoal, Consume
from django.http import JsonResponse


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "app/register.html", {"form": form})


@login_required
def add_food(request):
    if request.method == "POST":
        form = FoodForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = FoodForm()
    return render(request, "app/add_food.html", {"form": form})


@login_required
def update_goals(request):
    goal, created = HealthGoal.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = HealthGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = HealthGoalForm(instance=goal)
    return render(request, "app/update_goals.html", {"form": form})


@login_required
def index(request):
    all_foods = Food.objects.all()

    return render(request, "app/index.html", {"foods": all_foods})


@login_required
def chart_data(request):
    consumed = Consume.objects.filter(user=request.user)

    goal, _ = HealthGoal.objects.get_or_create(user=request.user)

    data = {
        "labels": [c.food_consumed.name for c in consumed],
        "carbs": [c.food_consumed.carbs for c in consumed],
        "proteins": [c.food_consumed.proteins for c in consumed],
        "fats": [c.food_consumed.fats for c in consumed],
        "calories": [c.food_consumed.calories for c in consumed],
        "goal_carbs": goal.carb_goal,
        "goal_proteins": goal.protein_goal,
        "goal_fats": goal.fat_goal,
        "goal_calories": goal.daily_calorie_goal,
    }
    return JsonResponse(data)