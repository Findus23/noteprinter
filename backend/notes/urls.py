from django.urls import path

from . import views

urlpatterns = [
    path("tokens", views.my_token_view, name="my_token_view"),
    path("unprinted", views.get_unprinted, name="get_unprinted"),
    path("edits/", views.viewedits, name="viewedits"),
    path("note/<int:note_id>", views.note_to_print, name="note_to_print"),
    path("note/<int:note_id>/printed", views.set_printed, name="set_printed"),
]
