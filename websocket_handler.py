import json
import websockets
import asyncio
from astralAideKillbot.embed_creator import send_killmail_embed
from astralAideKillbot.config import TARGET_ENTITY, TARGET_ENTITY_ID
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

async def subscribe_to_websocket(bot):
  uri = "wss://zkillboard.com/websocket/"
  payload = {
    "action": "sub",
    "channel": f"{TARGET_ENTITY}:{TARGET_ENTITY_ID}"
    # "channel":"all:*"
  }
  while True:
    try:
      async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(payload))
        print(f"Sent: {json.dumps(payload)}")

        async for message in websocket:
          data = json.loads(message)
          await asyncio.create_task(send_killmail_embed(bot, data))  # Pass bot to the embed function

    except (ConnectionClosedError, ConnectionClosedOK) as e:
        print(f"WebSocket connection closed: {e}")
        print("Attempting to reconnect...")
        await asyncio.sleep(5)  # Wait for a bit before reconnecting

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Attempting to reconnect...")
        await asyncio.sleep(5)  # Wait for a bit before reconnecting
