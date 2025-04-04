import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect

from .filters import ExpenseFilter
from .forms import ExpenseForm, CategoryForm, GroupExpenseForm
from .models import Expense, Category, GroupExpense


@login_required
def index(request):
    if request.method == "POST":
        expense_form = ExpenseForm(request.POST, user=request.user)
        if expense_form.is_valid():
            expense_obj = expense_form.save(commit=False)
            expense_obj.user = request.user
            expense_obj.save()
            return redirect('index')

    qs = Expense.objects.filter(user=request.user)
    expense_filter = ExpenseFilter(request.GET, queryset=qs, user=request.user)
    expenses = expense_filter.qs

    # expenses = Expense.objects.filter(user=request.user)
    total_expenses = expenses.aggregate(Sum('amount'))

    last_year = datetime.date.today() - datetime.timedelta(days=365)
    data = Expense.objects.filter(date__gt=last_year, user=request.user)
    yearly_sum = data.aggregate(Sum('amount'))

    last_month = datetime.date.today() - datetime.timedelta(days=30)
    data = Expense.objects.filter(date__gt=last_month, user=request.user)
    monthly_sum = data.aggregate(Sum('amount'))

    last_week = datetime.date.today() - datetime.timedelta(days=7)
    data = Expense.objects.filter(date__gt=last_week, user=request.user)
    weekly_sum = data.aggregate(Sum('amount'))

    daily_sums = Expense.objects.filter(user=request.user).values('date').order_by('date').annotate(sum=Sum('amount'))

    categorical_sums = Expense.objects.filter(user=request.user).values('category').order_by('category').annotate(sum=Sum('amount'))

    expense_form = ExpenseForm(user=request.user)
    return render(request, 'myapp/index.html',
                  {'expense_form': expense_form, 'expenses': expenses, 'expense_filter': expense_filter,
                   'total_expenses': total_expenses,
                   'yearly_sum': yearly_sum, 'monthly_sum': monthly_sum, 'weekly_sum': weekly_sum,
                   'daily_sums': daily_sums,
                   'categorical_sums': categorical_sums})


@login_required
def edit(request, id):
    expense = Expense.objects.get(id=id, user=request.user)
    expense_form = ExpenseForm(instance=expense)

    if request.method == "POST":
        expense = Expense.objects.get(id=id)
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid:
            form.save()
            return redirect('index')
    return render(request, 'myapp/edit.html', {'expense_form': expense_form})


@login_required
def delete(request, id):
    if request.method == "POST" and 'delete' in request.POST:
        expense = Expense.objects.get(id=id, user=request.user)
        expense.delete()
    return redirect('index')




@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            return redirect('category_list')
    return render(request, 'myapp/category_list.html', {'categories': categories, 'form': form})



@login_required
def group_expense_list(request):
    expenses = GroupExpense.objects.filter(users=request.user)
    return render(request, 'myapp/group_expense_list.html', {'expenses': expenses})


@login_required
def add_group_expense(request):
    if request.method == 'POST':
        form = GroupExpenseForm(request.POST)
        if form.is_valid():
            group_expense = form.save()
            return redirect('group_expense_list')
    else:
        form = GroupExpenseForm()
    return render(request, 'myapp/add_group_expense.html', {'form': form})