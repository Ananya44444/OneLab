from django.urls import path

from .views import chat_page, chat_view

urlpatterns = [
    path("", chat_page, name="chat_page"),
    path("api/chat/", chat_view, name="chat_view"),
]
