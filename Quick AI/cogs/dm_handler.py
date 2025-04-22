import disnake
from disnake.ext import commands
import re
import asyncio
import os

from utils.embeds import Embeds
from utils.database import Database
from utils.pollinations_api import PollinationsHandler

class DMHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.pollinations = PollinationsHandler()
        
        # Discord server invite link for premium
        self.premium_invite_link = "https://discord.gg/bQc7vw328d"
        
        # Image generation pattern
        self.image_pattern = re.compile(r'^(?:/image|/تصویر)\s+(.+)$', re.IGNORECASE)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages and non-DM messages
        if message.author.bot or not isinstance(message.channel, disnake.DMChannel):
            return
        
        # Process the message
        await self.process_dm(message)
    
    async def process_dm(self, message):
        """Process a DM message"""
        # Check if this is an image generation request
        image_match = self.image_pattern.match(message.content)
        
        if image_match:
            # This is an image generation request
            prompt = image_match.group(1).strip()
            await self.generate_image(message, prompt)
        else:
            # This is a text generation request
            await self.generate_text(message)
    
    async def generate_image(self, message, prompt):
        """Generate an image using pollinations API"""
        # Get user settings
        settings = self.db.get_user_settings(message.author.id)
        image_model = settings.get('image_model', 'flux')
        
        # Check premium status
        is_premium = self.db.is_premium_user(message.author.id)
        
        # Check if the selected model is premium
        is_premium_model = self.pollinations.is_premium_model(image_model, "image")
        
        if is_premium_model and not is_premium:
            await message.channel.send(
                embed=Embeds.error(
                    "✨ مدل پریمیوم",
                    f"این مدل فقط برای کاربران پریمیوم در دسترس است. برای خرید اشتراک پریمیوم به سرور ما بپیوندید:\n{self.premium_invite_link}"
                )
            )
            
            # Suggest free models
            free_models = self.pollinations.get_free_image_models()
            if free_models:
                free_models_str = "\n".join([f"• **{model}**: {data['description']}" for model, data in free_models.items()])
                await message.channel.send(
                    embed=Embeds.info(
                        "⭐ مدل‌های رایگان",
                        f"شما می‌توانید از مدل‌های رایگان زیر استفاده کنید:\n{free_models_str}"
                    )
                )
            return
        
        # Check if user has reached daily limit
        has_reached_limit, current_usage, limit = self.db.check_usage_limits(message.author.id, "image")
        
        if has_reached_limit:
            await message.channel.send(
                embed=Embeds.error(
                    "🔒 محدودیت روزانه",
                    f"شما به محدودیت روزانه تولید تصویر رسیده‌اید ({limit} تصویر در روز).\n\n"
                    f"برای دسترسی نامحدود به تمام مدل‌ها، اشتراک پریمیوم تهیه کنید:\n{self.premium_invite_link}"
                )
            )
            return
        
        # Increment usage counter (only for non-premium users)
        if not is_premium:
            self.db.increment_usage(message.author.id, "image")
            
            # Get updated usage information
            _, current_usage, limit = self.db.check_usage_limits(message.author.id, "image")
            
            # Notify user about remaining credits
            await message.channel.send(
                embed=Embeds.info(
                    "📊 اعتبار باقی‌مانده",
                    f"**{current_usage}** از **{limit}** درخواست تصویر امروز استفاده شده است."
                )
            )
        
        # Send typing indicator to show that the bot is processing
        async with message.channel.typing():
            # Send a waiting message
            waiting_msg = await message.channel.send(
                embed=Embeds.info(
                    "⏳ در حال تولید تصویر",
                    f"در حال تولید تصویر با پرامپت:\n```{prompt}```\nلطفاً صبر کنید..."
                )
            )
            
            try:
                # Generate the image
                result = self.pollinations.generate_image(prompt, model_name=image_model)
                
                if result.get('success', False):
                    # Get the image URL
                    image_url = result.get('url')
                    
                    if image_url:
                        # Send the image
                        await message.channel.send(
                            embed=Embeds.image_response(prompt, image_url, message.author)
                        )
                    else:
                        # No image URL
                        await message.channel.send(
                            embed=Embeds.error(
                                "❌ خطا در تولید تصویر",
                                "متأسفانه تصویری تولید نشد. لطفاً با پرامپت دیگری امتحان کنید."
                            )
                        )
                else:
                    # Error generating the image
                    error = result.get('error', 'خطای ناشناخته')
                    await message.channel.send(
                        embed=Embeds.error(
                            "❌ خطا در تولید تصویر",
                            f"خطایی رخ داد:\n```{error}```"
                        )
                    )
            except Exception as e:
                # Exception during image generation
                await message.channel.send(
                    embed=Embeds.error(
                        "❌ خطای سیستمی",
                        f"خطایی در سیستم رخ داد:\n```{str(e)}```"
                    )
                )
            finally:
                # Delete the waiting message
                try:
                    await waiting_msg.delete()
                except:
                    pass
    
    async def generate_text(self, message):
        """Generate text using pollinations API"""
        # Get user settings
        settings = self.db.get_user_settings(message.author.id)
        text_model = settings.get('text_model', 'openai')
        agent = settings.get('agent', 'agent-1')
        
        # Check premium status
        is_premium = self.db.is_premium_user(message.author.id)
        
        # Check if the selected model is premium
        is_premium_model = self.pollinations.is_premium_model(text_model, "text")
        
        if is_premium_model and not is_premium:
            await message.channel.send(
                embed=Embeds.error(
                    "✨ مدل پریمیوم",
                    f"این مدل فقط برای کاربران پریمیوم در دسترس است. برای خرید اشتراک پریمیوم به سرور ما بپیوندید:\n{self.premium_invite_link}"
                )
            )
            
            # Suggest free models
            free_models = self.pollinations.get_free_text_models()
            if free_models:
                free_models_str = "\n".join([f"• **{model['name']}**: {model['description']}" for model in free_models])
                await message.channel.send(
                    embed=Embeds.info(
                        "⭐ مدل‌های رایگان",
                        f"شما می‌توانید از مدل‌های رایگان زیر استفاده کنید:\n{free_models_str}"
                    )
                )
            return
        
        # Check if user has reached daily limit
        has_reached_limit, current_usage, limit = self.db.check_usage_limits(message.author.id, "text")
        
        if has_reached_limit:
            await message.channel.send(
                embed=Embeds.error(
                    "🔒 محدودیت روزانه",
                    f"شما به محدودیت روزانه پیام‌های متنی رسیده‌اید ({limit} پیام در روز).\n\n"
                    f"برای دسترسی نامحدود به تمام مدل‌ها، اشتراک پریمیوم تهیه کنید:\n{self.premium_invite_link}"
                )
            )
            return
        
        # Increment usage counter (only for non-premium users)
        if not is_premium:
            self.db.increment_usage(message.author.id, "text")
            
            # Get updated usage information
            _, current_usage, limit = self.db.check_usage_limits(message.author.id, "text")
            
            # Notify user about remaining credits
            await message.channel.send(
                embed=Embeds.info(
                    "📊 اعتبار باقی‌مانده",
                    f"**{current_usage}** از **{limit}** درخواست متنی امروز استفاده شده است."
                )
            )
        
        # Send typing indicator to show that the bot is processing
        async with message.channel.typing():
            try:
                # Generate the text
                response = self.pollinations.generate_text(
                    prompt=message.content, 
                    model_name=text_model,
                    agent=agent
                )
                
                if response:
                    # Split long responses
                    if len(response) > 2000:
                        chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                        for i, chunk in enumerate(chunks):
                            # Only the first chunk gets the title
                            await message.channel.send(
                                embed=Embeds.response(chunk, message.author)
                            )
                    else:
                        await message.channel.send(
                            embed=Embeds.response(response, message.author)
                        )
                else:
                    # No response
                    await message.channel.send(
                        embed=Embeds.error(
                            "❌ خطا در تولید پاسخ",
                            "متأسفانه پاسخی دریافت نشد. لطفاً دوباره امتحان کنید."
                        )
                    )
            except Exception as e:
                # Exception during text generation
                await message.channel.send(
                    embed=Embeds.error(
                        "❌ خطای سیستمی",
                        f"خطایی در سیستم رخ داد:\n```{str(e)}```"
                    )
                )

def setup(bot):
    bot.add_cog(DMHandler(bot)) 