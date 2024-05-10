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
    path('my_applications/', view_applications, name='my_applications'),
    path('logout/', views.user_logout, name='logout'),
    path('search/', views.search_messages, name='search'),
    path('post_message/', views.send_message, name='send_message'),
    path('membership_requests/', views.membership_requests, name='membership_requests'),
    path('insert_vote/<int:application_id>/', views.insert_vote, name='insert_vote'),
    path('users/', views.users, name='users'),
    path('search_users/', views.search_users, name='search_users'),
    path('add_friend/<int:friend_id>/', add_friend, name='add_friend'),
    path('add_neighbor/<int:neighbor_id>/', add_neighbor, name='add_neighbor'),
    path('membership/',views.view_member_status, name='view_member_status'),
    path('list_friends/', views.list_friends, name='list_friends'),
    path('list_neighbors/', views.list_neighbors, name='list_neighbors'),
]


