from django.core.management.base import BaseCommand

from notes.models import Note
from notes.render_image import NoteRenderer


class Command(BaseCommand):

    def handle(self, *args, **options):
        note = Note.objects.first()
        nr = NoteRenderer(note)
        nr.render_note()
