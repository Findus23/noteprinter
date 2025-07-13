from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "notes/index.html")

def room(request, room_name):
    return render(request, "notes/room.html", {"room_name": room_name})

def viewedits(request):
    return render(request, "notes/viewedits.html")
