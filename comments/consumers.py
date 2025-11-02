import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Comment, Page


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.page_id = self.scope['url_route']['kwargs']['page_id']
        self.room_group_name = f'comments_page_{self.page_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # IMPORTANT: Accept the connection
        await self.accept()
        
        # Send confirmation message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to comment room'
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'typing':
                # Broadcast typing indicator
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_typing',
                        'username': data.get('username', 'Someone'),
                        'is_typing': data.get('is_typing', False)
                    }
                )
        except Exception as e:
            print(f"Error in receive: {e}")

    async def comment_message(self, event):
        """Send new comment to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'new_comment',
            'comment': event['comment']
        }))

    async def vote_update(self, event):
        """Send vote update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'vote_update',
            'comment_id': event['comment_id'],
            'net_votes': event['net_votes']
        }))

    async def user_typing(self, event):
        """Send typing indicator to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': event['username'],
            'is_typing': event['is_typing']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        
        # Allow anonymous for testing, but track user
        if self.user and not self.user.is_anonymous:
            self.room_group_name = f'notifications_{self.user.id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            # For testing: accept but don't add to group
            await self.accept()
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Authentication required for notifications'
            }))
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def notification_message(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'comment_id': event.get('comment_id'),
            'page_id': event.get('page_id')
        }))