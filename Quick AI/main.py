import disnake
from disnake.ext import commands
import os
import json
import sqlite3
from pathlib import Path

# Bot configuration
# Instead of loading from .env file, we define configuration directly here
BOT_CONFIG = {
    "token": "MTM1MjcyMDU5Nzk5Nzg1MDY5NQ.GG3Zks.sb23y1G_XovlaaP9ylTCmS-4IQhJ6xTdfa_IbE",  # Replace with your actual bot token
    "owner_ids": [1352720597997850695],  # Replace with actual owner IDs
    "prefix": "!",
    "default_text_model": "openai",
    "default_image_model": "flux",
    "free_daily_text_limit": 50,
    "free_daily_image_limit": 15,
    "premium_invite_link": "https://discord.gg/bQc7vw328d"
}

# Bot configuration
if not os.path.exists('config.json'):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(BOT_CONFIG, f, indent=4)
else:
    # Load existing config
    with open('config.json', 'r', encoding='utf-8') as f:
        existing_config = json.load(f)
        
        # Update with any new configuration items
        updated = False
        for key, value in BOT_CONFIG.items():
            if key not in existing_config:
                existing_config[key] = value
                updated = True
        
        # Save updated config if needed
        if updated:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(existing_config, f, indent=4)
        
        # Use the existing config
        BOT_CONFIG = existing_config

# Create data directory
if not os.path.exists('data'):
    os.makedirs('data')

# Initialize database
conn = sqlite3.connect('data/quickai.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS premium_users (
    user_id INTEGER PRIMARY KEY,
    expires_at TEXT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY,
    text_model TEXT DEFAULT "openai",
    image_model TEXT DEFAULT "flux",
    agent TEXT DEFAULT "agent-1"
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS usage_tracking (
    user_id INTEGER,
    date TEXT,
    text_requests INTEGER DEFAULT 0,
    image_requests INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, date)
)
''')

conn.commit()
conn.close()

# Set up intents
intents = disnake.Intents.default()
intents.message_content = True
intents.members = True

# Initialize bot
bot = commands.Bot(
    command_prefix=BOT_CONFIG['prefix'],
    intents=intents,
    test_guilds=None  # Set this to your test server ID for instant command sync
)

# Load cogs
def load_cogs():
    cogs_dir = Path("./cogs")
    if not cogs_dir.exists():
        cogs_dir.mkdir(parents=True)
    
    for cog_file in cogs_dir.glob("*.py"):
        if cog_file.name != "__init__.py":
            cog_name = f"cogs.{cog_file.stem}"
            try:
                bot.load_extension(cog_name)
                print(f"Loaded cog: {cog_name}")
            except Exception as e:
                print(f"Failed to load cog {cog_name}: {e}")

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")
    print(f"Serving {len(bot.guilds)} guilds")
    print(f"Free daily limits: {BOT_CONFIG['free_daily_text_limit']} text requests, {BOT_CONFIG['free_daily_image_limit']} image requests")
    await bot.change_presence(activity=disnake.Activity(
        type=disnake.ActivityType.listening, 
        name="/settings"
    ))

# Run bot
if __name__ == "__main__":
    load_cogs()
    bot.run(BOT_CONFIG["token"]) 