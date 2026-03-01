from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_notice, name='add_notice'),
    path('edit/<int:pk>/', views.edit_notice, name='edit_notice'),
    path('delete/<int:pk>/', views.delete_notice, name='delete_notice'),
    
]