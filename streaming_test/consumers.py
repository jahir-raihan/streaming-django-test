import json
import asyncio
import aiohttp
from channels.generic.websocket import AsyncWebsocketConsumer


class LiveStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract tab ID from the WebSocket URL
        self.tab_id = self.scope['url_route']['kwargs']['tab_id']

        self.session_id = None  # Session ID will be set from the first received message
        self.group_name = f"stream_{self.tab_id}"

        # Add this connection to a group for the tab
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove this connection from the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            # Parse the incoming message
            data = json.loads(text_data)
            prompt = data.get("prompt", "Default Prompt")
            self.session_id = data.get("session_id", f"session-{self.tab_id}")  # Generate default session ID

            # Start streaming data from the API
            await self.stream_from_api(prompt)
        except Exception as e:
            # Send an error message to the client if something goes wrong
            await self.send(
                text_data=json.dumps({"error": f"An error occurred: {str(e)}"})
            )

    async def stream_from_api(self, prompt):
        """Fetch data from the streaming API via POST and send it to the WebSocket."""
        url = "http://0.0.0.0:8001/api/chat/stream/"
        payload = {"message": prompt, "session_id": self.session_id}
        headers = {"Content-Type": "application/json"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:

                    if response.status == 200:
                        async for chunk in response.content:
                            try:
                                # Remove the "data: " prefix and decode JSON
                                clean_chunk = str(chunk.decode("utf-8").strip())

                                if clean_chunk.startswith("data:"):
                                    clean_chunk = clean_chunk[len("data:"):].strip()
                                # Parse the JSON content

                                data = json.loads(clean_chunk)

                                # Check if it's a streaming chunk and send to WebSocket
                                if data.get("status") == "streaming":
                                    await self.send(
                                        text_data=json.dumps(
                                            {
                                                "chunk": data["chunk"],
                                                "model": data["model"],
                                                "session_id": data["session_id"],
                                            }
                                        )
                                    )
                            except (json.JSONDecodeError, KeyError) as e:
                                continue

                    else:
                        await self.send(
                            text_data=json.dumps(
                                {"error": f"Failed to fetch stream: {response.status}"}
                            )
                        )
        except aiohttp.ClientError as e:
            # Handle connection errors
            await self.send(
                text_data=json.dumps({"error": f"Connection error: {str(e)}"})
            )
