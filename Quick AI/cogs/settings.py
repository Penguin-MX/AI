import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
import json
import os

from utils.embeds import Embeds
from utils.database import Database
from utils.pollinations_api import PollinationsHandler

class TextModelSelect(disnake.ui.StringSelect):
    def __init__(self, text_models, is_premium=False):
        options = []
        
        for model in text_models:
            model_premium = model.get("premium", True)
            
            # Skip premium models for non-premium users
            if model_premium and not is_premium:
                continue
                
            options.append(
                disnake.SelectOption(
                    label=model["name"],
                    description=model["description"][:100],  # Truncate if too long
                    emoji="📝"
                )
            )
            
            if len(options) >= 25:  # Discord max options limit
                break
                
        # If no options are available (not premium, all models are premium)
        if not options:
            options.append(
                disnake.SelectOption(
                    label="upgrade_to_premium",
                    description="✨ برای دسترسی به مدل‌های بیشتر اشتراک پریمیوم تهیه کنید",
                    emoji="✨"
                )
            )
                
        super().__init__(
            placeholder="📝 انتخاب مدل متن",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="text_model_select"
        )
        
    async def callback(self, interaction: disnake.MessageInteraction):
        # Get the selected value
        selected_value = self.values[0]
        
        # Check if user selected the upgrade option
        if selected_value == "upgrade_to_premium":
            await interaction.response.send_message(
                embed=Embeds.info(
                    "✨ ارتقا به اشتراک پریمیوم",
                    "برای دسترسی به مدل‌های بیشتر و امکانات ویژه، با ادمین در تماس باشید."
                ),
                ephemeral=True
            )
            return
        
        # Save the setting to the database
        db = Database()
        settings = db.save_user_settings(interaction.user.id, text_model=selected_value)
        
        await interaction.response.send_message(
            embed=Embeds.success(
                "✅ تنظیمات ذخیره شد",
                f"مدل متن به **{selected_value}** تغییر یافت."
            ),
            ephemeral=True
        )

class AgentSelect(disnake.ui.StringSelect):
    def __init__(self, agents):
        options = []
        
        for agent in agents:
            options.append(
                disnake.SelectOption(
                    label=agent["name"],
                    description=agent["description"][:100],  # Truncate if too long
                    emoji="🤖"
                )
            )
                
        super().__init__(
            placeholder="🤖 انتخاب عامل هوش مصنوعی",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="agent_select"
        )
        
    async def callback(self, interaction: disnake.MessageInteraction):
        # Get the selected value
        selected_value = self.values[0]
        
        # Save the setting to the database
        db = Database()
        settings = db.save_user_settings(interaction.user.id, agent=selected_value)
        
        await interaction.response.send_message(
            embed=Embeds.success(
                "✅ تنظیمات ذخیره شد",
                f"عامل هوش مصنوعی به **{selected_value}** تغییر یافت."
            ),
            ephemeral=True
        )

class ImageModelSelect(disnake.ui.StringSelect):
    def __init__(self, image_models, is_premium=False):
        options = []
        
        for model_id, model_data in image_models.items():
            model_premium = model_data.get("premium", True)
            
            # Skip premium models for non-premium users
            if model_premium and not is_premium:
                continue
                
            options.append(
                disnake.SelectOption(
                    label=model_id,
                    description=model_data["description"][:100],  # Truncate if too long
                    emoji="🖼️"
                )
            )
        
        # If no options are available (not premium, all models are premium)
        if not options:
            options.append(
                disnake.SelectOption(
                    label="upgrade_to_premium",
                    description="✨ برای دسترسی به مدل‌های بیشتر اشتراک پریمیوم تهیه کنید",
                    emoji="✨"
                )
            )
                
        super().__init__(
            placeholder="🖼️ انتخاب مدل تولید تصویر",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="image_model_select"
        )
        
    async def callback(self, interaction: disnake.MessageInteraction):
        # Get the selected value
        selected_value = self.values[0]
        
        # Check if user selected the upgrade option
        if selected_value == "upgrade_to_premium":
            await interaction.response.send_message(
                embed=Embeds.info(
                    "✨ ارتقا به اشتراک پریمیوم",
                    "برای دسترسی به مدل‌های بیشتر و امکانات ویژه، با ادمین در تماس باشید."
                ),
                ephemeral=True
            )
            return
        
        # Save the setting to the database
        db = Database()
        settings = db.save_user_settings(interaction.user.id, image_model=selected_value)
        
        await interaction.response.send_message(
            embed=Embeds.success(
                "✅ تنظیمات ذخیره شد",
                f"مدل تولید تصویر به **{selected_value}** تغییر یافت."
            ),
            ephemeral=True
        )

class SettingsView(disnake.ui.View):
    def __init__(self, is_premium=False):
        super().__init__(timeout=None)
        
        # Get models from pollinations API
        pollinations = PollinationsHandler()
        
        # Add the selects to the view
        self.add_item(TextModelSelect(pollinations.get_text_models(), is_premium))
        self.add_item(AgentSelect(pollinations.get_agents()))
        self.add_item(ImageModelSelect(pollinations.get_image_models(), is_premium))
        
    @disnake.ui.button(label="💾 ذخیره تنظیمات", style=disnake.ButtonStyle.success, custom_id="save_settings")
    async def save_settings(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message(
            embed=Embeds.success(
                "✅ تنظیمات ذخیره شد",
                "تمامی تنظیمات شما با موفقیت ذخیره شدند."
            ),
            ephemeral=True
        )

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.pollinations = PollinationsHandler()
    
    @commands.slash_command(
        name="settings",
        description="تنظیمات Quick AI"
    )
    async def settings(self, inter: ApplicationCommandInteraction):
        """Settings command for Quick AI"""
        # Check if the user is premium
        is_premium = self.db.is_premium_user(inter.user.id)
        
        # Create custom embed based on premium status
        embed = Embeds.settings()
        
        # Add premium status information
        if is_premium:
            premium_expiry = self.db.get_premium_expiry(inter.user.id)
            expiry_str = premium_expiry.strftime("%Y/%m/%d") if premium_expiry else "نامشخص"
            embed.add_field(
                name="✨ وضعیت اشتراک",
                value=f"شما دارای اشتراک پریمیوم هستید!\nتاریخ انقضا: {expiry_str}",
                inline=False
            )
        else:
            embed.add_field(
                name="⭐ وضعیت اشتراک",
                value="شما از نسخه رایگان استفاده می‌کنید.\nبرای دسترسی به مدل‌های بیشتر، اشتراک پریمیوم تهیه کنید.",
                inline=False
            )
        
        # Send the settings view
        await inter.response.send_message(
            embed=embed,
            view=SettingsView(is_premium),
            ephemeral=True
        )

def setup(bot):
    bot.add_cog(Settings(bot)) 