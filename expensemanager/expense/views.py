from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required 
from django.db.models import Sum,Avg,Count
from django.utils import timezone
from datetime import datetime

from expense.models import ExpenseCategory,Expense,Budget

# Create your views here.
def homepage(req):
    return render(req,"home.html")

def login(req):
    form = AuthenticationForm(req.POST or None)
    if req.method == "POST":
        username = req.POST.get("username")
        password = req.POST.get("password")
        user = authenticate(username = username, password = password)
        if user is not None:
            auth_login(req, user)
            return redirect('dashboard')
        else:
            print("invalid credentials")
    data ={
        "loginForm" : form
    }        
    return render(req,"login.html",data)

def register(req):
    form = UserCreationForm(req.POST or None)
    if req.method == "POST":
        if form.is_valid():
            print("FORM VALID")
            data = form.save(commit=False)
            data.first_name = req.POST.get("first_name", "")
            data.last_name = req.POST.get("last_name", "")
            data.email = req.POST.get("email", "")
            data.save()
            return redirect("login")
    data = {
        "registerForm": form
    }
    return render(req, "register.html", data)

def logout(req):
    auth_logout(req)
    return redirect('home')



@login_required
def dashboard(req):

    today = timezone.now().date()

    # Current user's current month expenses
    monthly_expenses = Expense.objects.filter(
        user=req.user,
        date__year=today.year,
        date__month=today.month
    )

    # Total, Average and Entries in one query
    stats = monthly_expenses.aggregate(
        total=Sum("amount"),
        average=Avg("amount"),
        entries=Count("id")
    )

    total_expenses = stats["total"] or 0
    average_expense = stats["average"] or 0
    total_entries = stats["entries"]

    # Current month's budget
    monthly_budget = Budget.objects.filter(
        user=req.user,
        month__year=today.year,
        month__month=today.month
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    # Remaining budget
    remaining_budget = max(monthly_budget - total_expenses,0)

    # Latest 5 expenses
    recent_expenses = (monthly_expenses.select_related("category").order_by("-date")[:5])

    # Category-wise report
    category_report = (monthly_expenses.values(
            "category__category_name",
            "category__category_icon"
        )
        .annotate(
            total=Sum("amount")
        )
        .order_by("-total")
    )

    data = {
        "monthly_budget": monthly_budget,
        "total_expenses": total_expenses,
        "remaining_budget": remaining_budget,
        "total_entries": total_entries,
        "average_expense": average_expense,
        "recent_expenses": recent_expenses,
        "category_report": category_report,
    }

    return render(req, "dashboard.html", data)

@login_required
def add_category(req):
    if req.method == "POST":
        category = ExpenseCategory()
        category.user = req.user
        category.category_name = req.POST.get("category_name")
        category.category_icon = req.POST.get("category_icon")
        category.save()
        return redirect("manage_category")

    return render(req,"add_category.html")


@login_required
def manage_category(req):
    categories = ExpenseCategory.objects.filter(user = req.user)
    data ={
            "categories" : categories
        }
    return render(req, "manage_category.html",data)


@login_required
def edit_category(req, id):
    category = ExpenseCategory.objects.get(id = id, user=req.user)
    data = {
        "category" : category
    }

    if req.method == "POST":
        category.category_name = req.POST.get("category_name")
        category.category_icon = req.POST.get("category_icon")
        category.save()
        return redirect("manage_category")
    return render(req,"edit_category.html",data)

@login_required
def delete_category(req, id):
    data={}
    try:
        category = ExpenseCategory.objects.get(id = id , user=req.user)
        category.delete()
        return redirect(manage_category)
    except ExpenseCategory.DoesNotExist:
        data['error'] = "category not found"

    return redirect(manage_category)    


@login_required
def add_expense(req):
    categories = ExpenseCategory.objects.filter(user = req.user)
    if req.method == "POST":
        expense = Expense()
        expense.user = req.user
        expense.category_id = req.POST.get("category")
        expense.amount = req.POST.get("amount")
        expense.description = req.POST.get("description")
        expense.date = req.POST.get("date")
        expense.payment_type = req.POST.get("payment_type")
        expense.save()
        return redirect("manage_expense")

    data ={
        "categories" : categories
    }

    return render(req,"add_expense.html",data)

@login_required
def manage_expense(req):
    expenses = Expense.objects.filter(user = req.user).order_by("-date")

    total_expenses = expenses.aggregate(total=Sum("amount"))["total"] or 0

    today = timezone.now().date()

    this_month = expenses.filter(date__year=today.year,date__month=today.month).aggregate(total=Sum("amount"))["total"] or 0

    average_expenses = expenses.aggregate(average=Avg("amount"))["average"] or 0

    total_entries=expenses.count()

    categories = ExpenseCategory.objects.filter(user=req.user)
    data = {
        "expenses" : expenses,
        "categories" : categories,
        "total_expenses" : total_expenses,
        "this_month" : this_month,
        "average_expenses" : average_expenses,
        "total_entries" : total_entries,

    }
    return render(req,"manage_expense.html",data)

@login_required
def filter_expense(req):
    expenses = Expense.objects.filter(user=req.user).order_by("-date") #current user ka sara expenses
    categories = ExpenseCategory.objects.filter(user=req.user)  #current user ki categories

    category_id = req.GET.get("category") # filter ki values
    payment_type = req.GET.get("payment_type")
    search = req.GET.get("search")
    from_date = req.GET.get("from_date")
    to_date = req.GET.get("to_date")

    if category_id:
        expenses = expenses.filter(category_id=category_id) #category ka filter
    if payment_type:
        expenses = expenses.filter(payment_type=payment_type) #payment_type ka filter
    if search:    
        expenses = expenses.filter(description__icontains=search) #description ka search
    if from_date:
        expenses = expenses.filter(date__gte=from_date) #from date filter
    if to_date:
        expenses = expenses.filter(date__lte=to_date) #to_date filter

    total_expenses = expenses.aggregate(total=Sum("amount"))["total"] or 0 #total expense dega 

    today = timezone.now().date()
    
    this_month = expenses.filter(date__year=today.year,date__month=today.month).aggregate(total=Sum("amount"))["total"] or 0
    
    average_expenses = expenses.aggregate(average=Avg("amount"))["average"] or 0
    
    total_entries=expenses.count()

    data = {
        "expenses" : expenses,
        "categories" : categories,
        "total_expenses" : total_expenses,
        "this_month" : this_month,
        "average_expenses" : average_expenses,
        "total_entries" : total_entries,
    }
    return render(req,"manage_expense.html",data)



@login_required
def edit_expense(req, id):
    expense = Expense.objects.get(id=id, user=req.user)
    categories = ExpenseCategory.objects.filter(user=req.user)
    data = {
        "expense" : expense,
        "categories" : categories,
    }
    if req.method == "POST":
        expense.category_id = req.POST.get("category")
        expense.amount = req.POST.get("amount")
        expense.description = req.POST.get("description")
        expense.date = req.POST.get("date")
        expense.payment_type = req.POST.get("payment_type")
        expense.save()
        return redirect(manage_expense)
    return render(req,"edit_expense.html",data)    


@login_required
def delete_expense(req, id):
    data={}
    try:
        expense = Expense.objects.get(id=id, user=req.user)
        expense.delete()
        redirect(manage_expense)
    except Expense.DoesNotExist:
        data['error'] = "expense not found"
    return redirect(manage_expense)  


@login_required
def set_budget(req):
    expense = Expense.objects.filter(user=req.user)
    categories = ExpenseCategory.objects.filter(user=req.user)
    if req.method == "POST":
        category_id = req.POST.get("category")
        amount = req.POST.get("amount")
        month = req.POST.get("month")
        category = ExpenseCategory.objects.get(id = category_id,user=req.user)
        budget = Budget(user=req.user,category=category,amount=amount,month=month)
        budget.save()
        return redirect("view_budget")
    data = {
        "expense" : expense,
        "categories" : categories,
    }
    return render(req,"set_budget.html",data)


@login_required
def view_budget(req):
    budgets = Budget.objects.filter(user=req.user)
    total_budget = budgets.aggregate(total=Sum("amount"))["total"] or 0 
    total_spend = 0
    for budget in budgets:
        spend = Expense.objects.filter(
            user=req.user,
            category=budget.category,
            date__year=budget.month.year,
            date__month=budget.month.month
        ).aggregate(total=Sum("amount"))["total"] or 0
        budget.spent = spend
        budget.remaining = budget.amount - spend
        total_spend += spend
    total_remaining = total_budget - total_spend
    budget_count = budgets.count()

    data = {
        "budgets": budgets,
        "total_budget": total_budget,
        "total_spend": total_spend,
        "total_remaining": total_remaining,
        "budget_count": budget_count,
    }
    return render(req, "view_budget.html", data)

@login_required
def edit_budget(req, id):
    budget = Budget.objects.get(id=id, user=req.user)
    categories = ExpenseCategory.objects.filter(user=req.user)
    if req.method == "POST":
        budget.category_id = req.POST.get("category")
        budget.amount = req.POST.get("amount")
        budget.month = req.POST.get("month")
        budget.save()
        return redirect("view_budget")
    data = {
        "budget": budget,
        "categories" : categories
    }
    return render(req, "edit_budget.html", data)

@login_required
def delete_budget(req, id):
    data={}
    try:
        budget = Budget.objects.get(id=id, user=req.user)
        budget.delete()
        redirect(view_budget)
    except Budget.DoesNotExist:
        data['error'] = "expense not found"
    return redirect(view_budget)    


@login_required
def reports(request):
    expenses = Expense.objects.filter( user=request.user).select_related("category")
    # Filters
    year = request.GET.get("year")
    month = request.GET.get("month")
    category = request.GET.get("category")
    payment_type = request.GET.get("payment_type")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if year:
        expenses = expenses.filter(date__year=year)

    if month:
        expenses = expenses.filter(date__month=month)

    if category:
        expenses = expenses.filter(category_id=category)

    if payment_type:
        expenses = expenses.filter(payment_type=payment_type)

    if from_date:
        expenses = expenses.filter(date__gte=from_date)

    if to_date:
        expenses = expenses.filter(date__lte=to_date)

    # Summary
    total_amount = expenses.aggregate(
        total=Sum("amount")
    )["total"] or 0

    average_amount = expenses.aggregate(
        avg=Avg("amount")
    )["avg"] or 0

    total_entries = expenses.count()

    # Cash / Online
    cash_amount = expenses.filter(
        payment_type="cash"
    ).aggregate(total=Sum("amount"))["total"] or 0

    online_amount = expenses.filter(
        payment_type="online"
    ).aggregate(total=Sum("amount"))["total"] or 0

    # Category wise
    category_report = expenses.values(
        "category__category_name",
        "category__category_icon"
    ).annotate(
        total=Sum("amount"),
        count=Count("id")
    ).order_by("-total")

    # Monthly
    monthly_report = expenses.values(
        "date__year",
        "date__month"
    ).annotate(
        total=Sum("amount"),
        count=Count("id")
    ).order_by("date__year", "date__month")

    categories = ExpenseCategory.objects.filter(
        user=request.user
    )

    data = {
        "expenses": expenses,

        "total_amount": total_amount,
        "average_amount": average_amount,
        "total_entries": total_entries,

        "cash_amount": cash_amount,
        "online_amount": online_amount,

        "category_report": category_report,
        "monthly_report": monthly_report,

        "categories": categories,

        "selected_year": year,
        "selected_month": month,
        "selected_category": category,
        "selected_payment_type": payment_type,
        "selected_from_date": from_date,
        "selected_to_date": to_date,
    }

    return render(request,"reports.html",data)