import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from pusher import Pusher

from .models import Message

# Initialize Pusher with your credentials
pusher = Pusher(app_id='1787840', key='1787840', secret='9a1c28444674bc62a35f', cluster='eu')

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print("connect method called")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(f"room_name: {self.room_name}")
        self.room_group_name = 'webapp_viewer_%s' % self.room_name
        print(f"room_group_name: {self.room_group_name}")

        print(f"WebSocket connection established for room: {self.room_name}")

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

    self.accept()
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']
        receiver = text_data_json['receiver']

        # Save the message to the database
        new_message = Message.objects.create(
            sender=User.objects.get(username=sender),
            receiver=User.objects.get(username=receiver),
            content=message
        )

        # Trigger the 'new_message' event on the Pusher channel
        pusher.trigger(self.room_group_name, 'new_message', {
            'message': message,
            'sender': sender,
            'receiver': receiver
        })
        print(f"Received message: {message} from {sender} to {receiver}")

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'receiver': receiver
        }))
