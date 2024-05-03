# chat/consumers.py
import json
import time
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from . import models
from . import serializers

class IndexConsumer(WebsocketConsumer):
    def connect(self):
        self.all_connections_group = "global_group"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.all_connections_group, self.channel_name
        )

        rooms = models.DiscussionRoom.objects.all()

        rooms = serializers.RoomSerializer(rooms, many=True).data

        async_to_sync(self.channel_layer.group_send)(
            self.all_connections_group,  # group name
            {"type": "rooms.show", "rooms": rooms}
        )



        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        room_name = text_data_json["room_name"]

        try:
            room = models.DiscussionRoom.objects.get(name=room_name)
            self.send(text_data=json.dumps({"error": f"Room with name: {room_name} already exists"}))
        except models.DiscussionRoom.DoesNotExist:
            room = models.DiscussionRoom.objects.create(name=room_name)
            rooms = models.DiscussionRoom.objects.all()
            rooms = serializers.RoomSerializer(rooms, many=True).data

            async_to_sync(self.channel_layer.group_send)(
                self.all_connections_group,  # group name
                {"type": "rooms.show", "rooms": rooms}
            )



    def rooms_show(self, event):
        self.send(text_data=json.dumps(event))


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
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sent_by = self.scope["user"].username
        data = {
            "message":message,
            "sent_by":sent_by
        }
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", 'data': data}
        )

    # Receive message from room group
    def chat_message(self, event):
        data = event["data"]

        # Send message to WebSocket
      
        self.send(text_data=json.dumps({"data": data}))