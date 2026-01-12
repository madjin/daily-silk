import discord
import json
import os
import argparse
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

class Config:
    """Centralized configuration"""
    TOKEN = os.getenv("DISCORD_TOKEN")
    CHANNEL_ID = 1326603270893867064
    DATA_DIR = "data"

class MessageParser:
    """Handles message parsing and formatting"""
    
    @staticmethod
    def normalize_timestamp(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def create_content_key(data: Dict) -> str:
        desc = data.get('description', '') or ''
        return desc[:100]
    
    @staticmethod
    def parse_embed(embed: discord.Embed, timestamp: datetime) -> Dict:
        data = {
            "timestamp": MessageParser.normalize_timestamp(timestamp),
            "description": embed.description if embed.description else None
        }
        if embed.title:
            data["description"] = f"# {embed.title}\n\n{data['description']}" if data["description"] else f"# {embed.title}"
        data["content_key"] = MessageParser.create_content_key(data)
        return data

class DataManager:
    """Manages data storage and deduplication"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
    
    def load_existing(self, filename: str, clear: bool) -> List[Dict]:
        filepath = os.path.join(self.data_dir, filename)
        if clear or not os.path.exists(filepath):
            return []
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    item["content_key"] = MessageParser.create_content_key(item)
                print(f"Loaded {len(data)} existing entries from {filename}")
                return data
        except json.JSONDecodeError:
            print(f"Invalid JSON in {filename}. Starting fresh.")
            return []
    
    def save_data(self, filename: str, data: List[Dict]) -> None:
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Save JSON
        json_filepath = os.path.join(self.data_dir, filename)
        json_data = [{"timestamp": item["timestamp"], "description": item["description"]} 
                    for item in data]
        with open(json_filepath, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(data)} unique entries to {json_filepath}")
        
        # Save Markdown
        md_filename = os.path.splitext(filename)[0] + ".md"
        md_filepath = os.path.join(self.data_dir, md_filename)
        with open(md_filepath, "w", encoding="utf-8") as f:
            # Add header with date
            date_str = os.path.splitext(filename)[0]
            f.write(f"# Daily Summary for {date_str}\n\n")
            for item in data:
                f.write(f"## {item['timestamp']}\n\n")
                f.write(f"{item['description']}\n\n")
        print(f"Exported {len(data)} entries to {md_filepath}")

class DiscordFetcher:
    """Handles Discord interactions and message fetching"""
    
    def __init__(self, config: Config, data_manager: DataManager):
        self.config = config
        self.data_manager = data_manager
        intents = discord.Intents.default()
        intents.messages = True
        self.client = discord.Client(intents=intents)
        self._register_events()
    
    def _register_events(self):
        @self.client.event
        async def on_ready():
            print(f'Logged in as {self.client.user}')
            await self._fetch_messages()
            await self.client.close()
    
    async def _fetch_messages(self):
        channel = self.client.get_channel(self.config.CHANNEL_ID)
        if not channel:
            print(f"Channel {self.config.CHANNEL_ID} not found")
            return
        
        args = self._parse_args()
        end_date = (datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=timezone.utc) 
                   if args.date else datetime.now(timezone.utc))
        start_date = end_date - timedelta(days=args.days - 1)  # Include end_date
        
        print(f"Fetching messages from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        messages_by_date = await self._collect_messages(channel, start_date, end_date)
        
        for date_str, messages in messages_by_date.items():
            filename = f"{date_str}.json"
            existing_data = self.data_manager.load_existing(filename, args.clear)
            all_data = messages if args.clear else existing_data + messages
            filtered_data = self._filter_and_sort(all_data)
            self.data_manager.save_data(filename, filtered_data)
    
    async def _collect_messages(self, channel: discord.TextChannel, 
                              start_date: datetime, 
                              end_date: datetime) -> Dict[str, List[Dict]]:
        messages_by_date = {}
        content_keys_by_date = {d.strftime("%Y-%m-%d"): set() 
                              for d in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1))}
        
        async for msg in channel.history(limit=None, after=start_date - timedelta(days=1), before=end_date + timedelta(days=1)):
            date_str = msg.created_at.strftime("%Y-%m-%d")
            if date_str not in content_keys_by_date:
                continue
            
            if date_str not in messages_by_date:
                messages_by_date[date_str] = []
            
            for embed in msg.embeds:
                msg_data = MessageParser.parse_embed(embed, msg.created_at)
                if msg_data["content_key"] not in content_keys_by_date[date_str]:
                    messages_by_date[date_str].append(msg_data)
                    content_keys_by_date[date_str].add(msg_data["content_key"])
        
        total_new = sum(len(msgs) for msgs in messages_by_date.values())
        print(f"Found {total_new} new messages across {len(messages_by_date)} days")
        return messages_by_date
    
    def _filter_and_sort(self, data: List[Dict]) -> List[Dict]:
        filtered = []
        seen_keys = set()
        for item in data:
            if "content_key" not in item:
                item["content_key"] = MessageParser.create_content_key(item)
            if item["content_key"] not in seen_keys:
                filtered.append(item)
                seen_keys.add(item["content_key"])
        
        # Sort from start of day to end of day (earliest to latest)
        filtered.sort(key=lambda x: x["timestamp"])  # Changed to ascending order
        removed = len(data) - len(filtered)
        if removed > 0:
            print(f"Filtered out {removed} duplicate entries")
        return filtered
    
    def _parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description='Fetch Discord messages')
        parser.add_argument('--date', help='End date to fetch (YYYY-MM-DD), defaults to today')
        parser.add_argument('--days', type=int, default=1, 
                          help='Number of days to fetch, ending at target date (default: 1)')
        parser.add_argument('--clear', action='store_true',
                          help='Clear existing files before adding new data')
        return parser.parse_args()
    
    def run(self):
        self.client.run(self.config.TOKEN)

def main():
    config = Config()
    data_manager = DataManager(config.DATA_DIR)
    fetcher = DiscordFetcher(config, data_manager)
    fetcher.run()

if __name__ == "__main__":
    main()
