from attendance import views
from django.urls import path, include

app_name = 'attendance'
urlpatterns = [
    path('attendance/', views.index),
    path('', views.accueil),
    path('video_feed/', views.video_feed, name='video-feed'),
    path('toggle_camera/', views.toggle_camera, name='toggle-camera'),
    path('toggle_recognition', views.toggle_recognition, name='toggle-recognition'),
    path('recognize_and_register/', views.recognize_and_register, name='recognize-and-register'),

]
