import discord
import json
import asyncio
from datetime import datetime
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Get token from environment variable
CHANNEL_ID = 1326603270893867064  # Replace with actual channel ID

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel = client.get_channel(CHANNEL_ID)

    messages_data = []

    if channel:
        async for msg in channel.history(limit=10):
            for embed in msg.embeds:
                embed_data = {
                    "timestamp": msg.created_at.isoformat(),
                    "title": embed.title if embed.title else None,
                    "description": embed.description if embed.description else None,
                }
                messages_data.append(embed_data)

    # Generate timestamp for filename (YYYYMMDD)
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)  # Create data folder if it doesn't exist
    output_file = f"{output_dir}/{timestamp}.json"

    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(messages_data, f, indent=2, ensure_ascii=False)

    print(f"Data saved to {output_file}")
    await client.close()

if __name__ == "__main__":
    client.run(TOKEN)
