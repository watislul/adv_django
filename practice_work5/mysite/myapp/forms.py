from django.forms import ModelForm
from .models import Expense, Category, GroupExpense


class ExpenseForm(ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'amount', 'category']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['category'].queryset = Category.objects.filter(user=user)


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name']



class GroupExpenseForm(ModelForm):
    class Meta:
        model = GroupExpense
        fields = ['name', 'amount', 'users']