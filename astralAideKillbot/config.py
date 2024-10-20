from dotenv import load_dotenv
import os

load_dotenv()

TARGET_ENTITY_ID = os.getenv("TARGET_ENTITY_ID")
TARGET_DISCORD_CHANNEL_ID = int(os.getenv("TARGET_DISCORD_CHANNEL_ID"))
TARGET_ENTITY = os.getenv('TARGET_ENTITY')
TOKEN = os.getenv("TOKEN")
DELAY = 3
CONCURRENT_TASK = int(os.getenv("CONCURRENT_TASK", 5))