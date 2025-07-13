import channels
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        print("bla")
        channel_layer=get_channel_layer()
        print(channel_layer)
        # async_to_sync(channel_layer.send)("chat_test", "test")
        for i in range(100):
            async_to_sync(channel_layer.group_send)("chat_test", {"type": "chat.message", "message": f"hello{i}"})
