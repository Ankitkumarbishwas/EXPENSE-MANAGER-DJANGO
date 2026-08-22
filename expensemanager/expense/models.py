from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# Create your models here.

class ExpenseCategory(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="expense_categories")
    category_name = models.CharField(max_length=50)
    category_icon = models.CharField(max_length=10,default="📦")

    def __str__(self):
        return f"{self.category_icon} {self.category_name}"


class Expense(models.Model):
    CASH = 'cash'
    ONLINE = 'online'
    PAYMENT_TYPE_CHOICES = [
        (CASH,'cash'),
        (ONLINE,'online'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    description = models.TextField(blank=True,default= "N/A")
    date = models.DateField()
    payment_type = models.CharField(max_length=10,choices=PAYMENT_TYPE_CHOICES,default=CASH)

    def __str__(self):
        return f"{self.category.category_name} ₹{self.amount}"

class Budget(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    month = models.DateField()

    def __str__ (self):
        return f"{self.category.category_name} ₹{self.amount}"