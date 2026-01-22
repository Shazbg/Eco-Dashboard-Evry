# apps/alimentation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.foodentry_list, name='food_list'),
    path('nouveau/', views.foodentry_create, name='food_form'),
]
