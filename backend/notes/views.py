from base64 import b64encode

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from notes.forms import NoteForm
from notes.models import Note, APIToken


@login_required
def viewedits(request):
    return render(request, "notes/viewedits.html")


@login_required
def main(request):
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("main")
    else:
        form = NoteForm()

    notes = Note.objects.all().order_by("-created_at")[:100]

    return render(request, "notes/main.html", {
        "notes": notes,
        "form": form,
    })


@login_required
@require_POST
def add_note(request):
    form = NoteForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("main")


@login_required
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


@login_required
@csrf_exempt
@require_POST
def set_printed(request, note_id):
    note = Note.objects.get(id=note_id)
    now = timezone.now()
    note.printed_at = now
    note.save(skip_notify=True)
    return JsonResponse({"message": "success"})


@login_required
def my_token_view(request):
    token, _ = APIToken.objects.get_or_create(user=request.user)
    return JsonResponse({"token": token.key})


@login_required
@csrf_exempt
def get_unprinted(request):
    notes = Note.objects.filter(printed_at=None).order_by("created_at")
    note_ids = [note.id for note in notes]
    return JsonResponse({"note_ids": note_ids})
