"""
URL configuration for expensemanager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from expense import views

# for using image
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.homepage, name="home"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("features/", views.features, name="features"),
    path("howitswork/", views.howitswork, name="howitswork"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    #category
    path("add_category/", views.add_category, name="add_category"),
    path("manage_category/", views.manage_category, name="manage_category"),
    path("edit_category/<int:id>/", views.edit_category, name="edit_category"),
    path("delete_category/<int:id>/", views.delete_category, name="delete_category"),

    #Expense
    path("add_expense/", views.add_expense, name="add_expense"),
    path("manage_expense/", views.manage_expense, name="manage_expense"),
    path("edit_expense/<int:id>/", views.edit_expense, name="edit_expense"),
    path("delete_expense/<int:id>/", views.delete_expense, name="delete_expense"),
    path("filter_expense", views.filter_expense, name="filter_expense"),
    path("edit_expense/<int:id>/", views.edit_expense, name="edit_expense"),
    path("delete_expense/<int:id>/", views.delete_expense, name="delete_expense"),

    #set budget
    path("set_budget/", views.set_budget, name="set_budget"),
    path("view_budget/", views.view_budget, name="view_budget"),
    path("edit_budget/<int:id>/", views.edit_budget, name="edit_budget"),
    path("delete_budget/<int:id>/", views.delete_budget, name="delete_budget"),

    #Reports
    path("reports/",views.reports,name="reports"),

    #Excel downloard reports
    path("downloard-reports-excel/",views.download_reports_excel, name="download_reports_excel")
]

# append array for using images
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)