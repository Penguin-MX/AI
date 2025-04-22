# Quick AI Discord Bot

A Discord bot with red theme that uses the pollinations API for AI text and image generation.

## Features

- AI text generation using various models
- AI image generation using Flux and other models
- Premium user system with multiple subscription durations
- Free tier with daily usage limits (50 text requests, 15 image requests per day)
- Settings customization
- Persian language interface

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Edit `main.py` and update the BOT_CONFIG with your Discord bot token and owner IDs
4. Run the bot:
   ```
   python main.py
   ```

## Commands

- `/settings` - Open the settings menu
- `/check-premium` - Check your premium status and daily usage limits
- `/give-premium` - Give premium to a user (owner only)
  - Subscription durations: 1 day, 7 days, 1 month, 3 months, 1 year, 3 years, unlimited
- `/remove-premium` - Remove premium from a user (owner only)

## DM Commands

The bot is designed to work in DMs and will respond to any text message with AI-generated text.

- Type any message to get an AI response
- Use `/image [prompt]` or `/تصویر [prompt]` to generate an image

## Free vs Premium

### Free Tier
- Access to 4 basic AI models (marked with ⭐)
- 50 text requests per day
- 15 image requests per day
- Basic image generation (Flux model only)

### Premium Tier
- Unlimited usage of all models
- Access to all 22+ AI models (including premium models marked with ✨)
- Advanced image generation models
- Priority processing

## Configuration

Edit the `BOT_CONFIG` in the `main.py` file to configure the bot:

```python
BOT_CONFIG = {
    "token": "YOUR_TOKEN_HERE",  # Replace with your actual bot token
    "owner_ids": [123456789],  # Replace with actual owner IDs
    "prefix": "!",
    "default_text_model": "openai",
    "default_image_model": "flux",
    "free_daily_text_limit": 50,
    "free_daily_image_limit": 15,
    "premium_invite_link": "https://discord.gg/bQc7vw328d"
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Join Our Discord

For premium subscriptions and support, join our Discord server: https://discord.gg/bQc7vw328d 