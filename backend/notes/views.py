from base64 import b64encode

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from notes.models import Note


# Create your views here.
def index(request):
    return render(request, "notes/index.html")


def room(request, room_name):
    return render(request, "notes/room.html", {"room_name": room_name})


def viewedits(request):
    return render(request, "notes/viewedits.html")


def note_to_print(request, note_id):
    note = Note.objects.get(id=note_id)
    data = {
        "note_id": note.id,
        "created_at": note.created_at,
        "printed_at": note.printed_at,
    }
    if note.image:
        with note.image.image.file.open("rb") as image_file:
            encoded_string = b64encode(image_file.read()).decode()

        data["image"] = encoded_string
    return JsonResponse(data)

@csrf_exempt
@require_POST
def set_printed(request, note_id):
    note = Note.objects.get(id=note_id)
    now = timezone.now()
    note.printed_at = now
    note.save(skip_notify=True)
    return JsonResponse({"message": "success"})
