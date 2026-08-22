from django.contrib import admin
from expense.models import ExpenseCategory,Expense,Budget

# Register your models here.
admin.site.register(ExpenseCategory)
admin.site.register(Expense)
admin.site.register(Budget)