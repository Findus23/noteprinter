from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.utils.html import format_html


class Note(models.Model):
    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    printed_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return self.text[:50]

    def save(self, *args, **kwargs):
        just_setting_image = kwargs.pop("just_setting_image", False)
        super().save(*args, **kwargs)
        if just_setting_image:
            return
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)("saves", {"type": "forward.edit", "message": f"hello {self.text}"})
        async_to_sync(channel_layer.send)(
            "render-note",
            {
                "type": "render",
                "note_id": self.id,
            },
        )


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
