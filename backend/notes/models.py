import os

import binascii
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import models, transaction
from django.utils.html import format_html


class Note(models.Model):
    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    printed_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return self.text[:50]

    def save(self, *args, **kwargs):
        skip_notify = kwargs.pop("skip_notify", False)
        super().save(*args, **kwargs)
        conn = transaction.get_connection()
        print(conn.in_atomic_block)
        if skip_notify:
            return
        def notify():
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)("saves", {"type": "forward.edit", "message": f"hello {self.text}"})
            async_to_sync(channel_layer.send)(
                "render-note",
                {
                    "type": "render",
                    "note_id": self.id,
                },
            )
        transaction.on_commit(notify)


class NoteImage(models.Model):
    note = models.OneToOneField(Note, on_delete=models.CASCADE, null=True, blank=True, related_name="image")

    image = models.FileField(upload_to="notes")
    pdf_file = models.FileField(upload_to="notes")
    created_at = models.DateTimeField(auto_now_add=True)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()

    def image_preview(self):
        return format_html(
            '<img src="{}">',
            self.image.url,
        )


class APIToken(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = binascii.hexlify(os.urandom(20)).decode()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} → {self.key}"
