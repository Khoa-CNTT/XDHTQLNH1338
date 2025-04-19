import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class NotifyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handle WebSocket connection and dynamically assign to groups based on notification type.
        """
        self.notification_type = self.scope['url_route']['kwargs']['notification_type']
        self.group_name = f"{self.notification_type}_notifications"

        print(f"WebSocket connected to group: {self.group_name}")
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Remove the WebSocket connection from the specified group on disconnect.
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Handle incoming WebSocket data and process based on notification type.
        """
        data = json.loads(text_data)
        recipient_group = self.group_name

        data['message'] = 'Khách hàng A - Bàn 1 - đã gửi một đơn hàng!'
        # Broadcast the notification
        await self.channel_layer.group_send(
            recipient_group,
            {
                "type": "send_notification",
                "data": data,
            },
        )

    async def send_notification(self, event):
        """
        Send notification to all WebSocket connections in the group.
        """
        print("Notified")
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def get_user(self, user_id):
        """
        Fetch user object by user ID.
        """
        from django.contrib.auth.models import User
        return User.objects.get(id=user_id)

    # @database_sync_to_async
    # def create_notification(self, user, title, message, notification_type):
    #     """
    #     Create a notification record in the database.
    #     """
    #     from f1_web.models import Notification
    #     return Notification.objects.create(
    #         user=user,
    #         title=title,
    #         message=message,
    #         type=notification_type,
    #     )
