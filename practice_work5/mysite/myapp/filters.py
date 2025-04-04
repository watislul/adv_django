# myapp/filters.py
import django_filters
from .models import Expense, Category

class ExpenseFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='date', lookup_expr='gte', label='Date from'
    )
    end_date = django_filters.DateFilter(
        field_name='date', lookup_expr='lte', label='Date to'
    )

    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.none(),
        label='Category'
    )

    class Meta:
        model = Expense
        fields = ['start_date', 'end_date', 'category']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.filters['category'].queryset = Category.objects.filter(user=user)
