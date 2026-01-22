from django.urls import path
from . import views

urlpatterns = [
    path('form/', views.purchase_form, name='purchase_form'),
    path('list/', views.purchase_list, name='purchase_list'),
    path('<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('<int:pk>/delete/', views.purchase_delete, name='purchase_delete'),
]
