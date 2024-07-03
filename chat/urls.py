from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
     path('room/<str:room>/<str:username>/', views.room, name='room'),
    path('checkview/', views.checkview, name='checkview'),
    path('send', views.send, name='send'),
    path('getMessages/<str:room>/', views.getMessages, name='getMessages'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('create-room/', views.create_room, name='create_room'),
]
