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
    path('search/', views.search_messages, name='search'),
    path('post_message/', views.send_message, name='send_message'),
    path('membership_requests/', views.membership_requests, name='membership_requests'),
    path('approve_membership/<int:application_id>/', views.approve_membership, name='approve_membership'),
    path('reject_membership/<int:application_id>/', views.reject_membership, name='reject_membership'),
    path('users/', views.users, name='users'),
    path('search_users/', views.search_users, name='search_users'),
    path('add_neighbor/', views.add_neighbor, name='add_neighbor'),
    path('add_friend/', views.add_friend, name='add_friend'),


]


