import json
import time

from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.generic.websocket import WebsocketConsumer

from notes.models import Note
from notes.render_image import NoteRenderer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        if message == "hello":
            print("test")
            async_to_sync(self.channel_layer.send)(
                "thumbnails-generate",
                {
                    "type": "generate",
                    "id": 123456789,
                },
            )
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))


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

    # Receive message from room group
    def forward_edit(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))


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
