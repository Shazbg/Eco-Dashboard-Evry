from django.urls import path
from . import views

urlpatterns = [
    path('', views.purchase_list, name='purchase_list'),
    path('nouveau/', views.purchase_form, name='purchase_form'),
    path('<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('<int:pk>/supprimer/', views.purchase_delete, name='purchase_delete'),
]
