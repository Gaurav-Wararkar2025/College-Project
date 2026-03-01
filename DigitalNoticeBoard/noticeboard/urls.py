from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('add/', views.add_notice, name='add_notice'),
    path('edit/<int:pk>/', views.edit_notice, name='edit_notice'),
    path('delete/<int:pk>/', views.delete_notice, name='delete_notice'),
    path('notice/<int:pk>/', views.notice_detail, name='notice_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]