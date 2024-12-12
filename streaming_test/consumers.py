import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio


class LiveStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract tab ID from the WebSocket URL
        self.tab_id = self.scope['url_route']['kwargs']['tab_id']

        # Use the tab ID to create a unique group for the tab
        self.group_name = f"stream_{self.tab_id}"

        # Add the connection to the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the connection from the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Receive the prompt sent by the WebSocket client
        data = json.loads(text_data)
        prompt = data.get('prompt', 'Default Prompt')

        # Stream responses back to the client
        for i in range(1, 11):
            line = f"{prompt} - Line {i}: This is a dynamically generated streamed response."
            await self.send(text_data=json.dumps({'line': line}))
            await asyncio.sleep(0.3)  # Simulate delay
