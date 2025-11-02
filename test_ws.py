import os
import django
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comment_system.settings')
django.setup()

from channels.layers import get_channel_layer

async def test():
    channel_layer = get_channel_layer()
    print("Channel layer:", channel_layer)
    
    # Test sending message
    await channel_layer.group_send(
        "test_group",
        {
            "type": "test.message",
            "message": "Hello"
        }
    )
    print("✅ Channel layer working!")

asyncio.run(test())