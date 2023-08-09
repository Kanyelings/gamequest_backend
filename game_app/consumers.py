from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from game_app.models import Thread

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        # Creating individual chat rooms
        chat_room = f"user_chatroom_{user.id}"
        self.chat_room = chat_room
        # Join chat room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave chat room
        await self.channel_layer.group_discard(
            self.chat_room,
            self.channel_layer
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sender_username = text_data_json["username"]
        self_user = User.objects.get(username=sender_username)
        receiver_username = text_data_json["receiver_username"]
        receiver = User.objects.get(username=receiver_username)
        thread, created = Thread.objects.get_or_create(first_person=self_user, second_person=receiver)
        # Send message to chat room
        await self.channel_layer.group_send(
            self.chat_room,
            {
                "type": "sendmessage",
                "message": message,
                "sent_by": sender_username
            }
        )
        other_user_chat_room = f"user_chatroom_{receiver.id}"
        await self.channel_layer.group_send(
            other_user_chat_room,
            {
                "type": "sendmessage",
                "message": message,
                "sent_by": sender_username
            }
        )

    # Receive message from room group
    async def sendmessage(self, event):
        message = event["message"]
        username = event["username"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "sent_by": username}))
