from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_interface, name='chat_bot'),
    path('stream/', views.stream_chat_response, name='stream_chat_response'),
]