# urls.py
from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('blocks/', views.blocks, name='blocks'),
    path('search_blocks/', views.search_blocks, name='search_blocks'),
    path('insert_application/', views.insert_application, name='insert_application'),
    path('my_applications/', view_applications, name='view_applications'),
    path('logout/', views.user_logout, name='logout'),
]


