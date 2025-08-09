import json

import time
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.generic.websocket import WebsocketConsumer

from notes.models import Note
from notes.render_image import NoteRenderer


class SaveConsumer(WebsocketConsumer):
    def connect(self):
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            "saves", self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            "saves", self.channel_name
        )

    def forward_edit(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))


class PrinterConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.was_connected = False

    def connect(self):
        self.user = self.scope["user"]
        print(self.user)
        if not self.user.is_authenticated:
            self.close()
            return
        async_to_sync(self.channel_layer.group_add)(
            "printer", self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        if self.was_connected:
            async_to_sync(self.channel_layer.group_discard)(
                "printer", self.channel_name
            )

    def new_print(self, event):
        print(event)
        self.send(text_data=json.dumps({"message": "new_print", "note_id": event["note_id"]}))


class RenderConsumer(SyncConsumer):
    def render(self, data):
        note_id = data["note_id"]
        print(note_id)
        note = Note.objects.get(pk=note_id)
        nr = NoteRenderer(note)
        nr.render_note()


class PrintConsumer(SyncConsumer):
    def generate(self, message):
        print("Test: ", message)
        time.sleep(5)
        print("finished sleep")
