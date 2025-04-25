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

        notification_data = await self.create_notification(data)

        # Sau khi tạo xong notification → broadcast
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_notification",
                "data": notification_data,
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

    @database_sync_to_async
    def create_notification(self, data):
        from web_01.models import Notification, Session

        session = Session.objects.get(id=data['session']['session_id'])

        notification_type = data['type']
        table_number = session.table.table_number
        message_config = {
            'order_status': {
                'message': f'📦 Trạng thái đơn hàng từ bàn {table_number} - {session.customer.first_name}.',
                'level': 'info',
            },
            'promotion': {
                'message': '🎉 Ưu đãi mới vừa được cập nhật!',
                'level': 'success',
            },
            'reminder': {
                'message': f'⏰ Nhắc nhở cho bàn {table_number}.',
                'level': 'warning',
            },
            'custom': {
                'message': data.get('message', '🔔 Thông báo tuỳ chỉnh.'),
                'level': 'info',
            },
            'payment': {
                'message': f'💵 Thanh toán hoàn tất từ bàn {table_number} - {session.customer.first_name}.',
                'level': 'success',
            },
        }

        notification_type = data.get('type', 'custom')
        config = message_config.get(notification_type, message_config['custom'])

        # Lấy thông điệp phù hợp
        message = message_config.get(notification_type, '🔔 Bạn có một thông báo mới.')

        # Tạo notification trong DB (synchronous)
        Notification.objects.create(
            user=session.customer.user,
            type=notification_type,
            message=message,
            data={
                "session": session.id
            }
        )

        return {
            'type': notification_type,
            'message': config['message'],
            'level': config['level'],
            "data": data
        }
