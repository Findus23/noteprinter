from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path

from . import views


urlpatterns = [
    path("chat/", views.index, name="index"),
    path("chat/<str:room_name>/", views.room, name="room"),
    path("edits/", views.viewedits, name="room"),
]
