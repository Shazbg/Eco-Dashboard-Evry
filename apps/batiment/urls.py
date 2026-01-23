from django.urls import path
from . import views

urlpatterns = [
    path("", views.batiment_list_view, name="batiment_list"),
    path("nouveau/", views.batiment_form_view, name="batiment_form"),
    path('<int:pk>/', views.batiment_detail_view, name='batiment_detail'),
    path('<int:pk>/supprimer/', views.batiment_delete_view, name='batiment_delete'),
]
