import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction, Option, OptionType
import json
import os
from typing import List

from utils.embeds import Embeds
from utils.database import Database

class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        
        # Premium duration options
        self.duration_options = {
            "1_day": {"days": 1, "display": "1 روز", "emoji": "🕐"},
            "7_days": {"days": 7, "display": "7 روز", "emoji": "📅"},
            "1_month": {"days": 30, "display": "1 ماه", "emoji": "🗓️"},
            "3_months": {"days": 90, "display": "3 ماه", "emoji": "📆"},
            "1_year": {"days": 365, "display": "1 سال", "emoji": "🎂"},
            "3_years": {"days": 1095, "display": "3 سال", "emoji": "🏆"},
            "unlimited": {"days": 0, "display": "نامحدود", "emoji": "♾️"}
        }
        
        # Discord server invite link for premium
        self.premium_invite_link = "https://discord.gg/bQc7vw328d"
        
        # Load config for owner IDs
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    @commands.slash_command(
        name="give-premium",
        description="اعطای اشتراک پریمیوم به کاربر"
    )
    async def give_premium(
        self, 
        inter: ApplicationCommandInteraction,
        user_id: str = Option(
            name="user_id",
            description="آیدی کاربر",
            required=True
        ),
        duration: str = Option(
            name="duration",
            description="مدت اعتبار",
            required=True,
            choices={
                "1 روز": "1_day",
                "7 روز": "7_days",
                "1 ماه": "1_month",
                "3 ماه": "3_months",
                "1 سال": "1_year",
                "3 سال": "3_years",
                "نامحدود": "unlimited"
            }
        )
    ):
        """Give premium to a user with specified duration"""
        # Check if user is an owner
        if str(inter.user.id) not in [str(owner_id) for owner_id in self.config.get('owner_ids', [])]:
            await inter.response.send_message(
                embed=Embeds.error(
                    "❌ خطا",
                    "شما دسترسی لازم برای استفاده از این دستور را ندارید."
                ),
                ephemeral=True
            )
            return
            
        try:
            # Try to convert user_id to int
            user_id = int(user_id)
            
            # Get duration days
            days = self.duration_options[duration]["days"]
            duration_display = self.duration_options[duration]["display"]
            
            # Add premium to user
            expires_at = self.db.add_premium_user(user_id, days)
            
            # Fetch user object if possible
            user = self.bot.get_user(user_id)
            user_mention = f"<@{user_id}>" if not user else user.mention
            
            await inter.response.send_message(
                embed=Embeds.success(
                    "✅ اشتراک پریمیوم اعطا شد",
                    f"اشتراک پریمیوم با موفقیت به کاربر {user_mention} به مدت {duration_display} اعطا شد."
                ),
                ephemeral=True
            )
            
            # Try to notify the user
            if user:
                try:
                    await user.send(
                        embed=Embeds.success(
                            "✨ اشتراک پریمیوم فعال شد",
                            f"اشتراک پریمیوم شما به مدت {duration_display} فعال شد!\n"
                            "اکنون می‌توانید از تمامی مدل‌ها بدون محدودیت استفاده کنید."
                        )
                    )
                except:
                    # Failed to DM user, just continue
                    pass
                
        except ValueError:
            await inter.response.send_message(
                embed=Embeds.error(
                    "❌ خطا",
                    "آیدی کاربر باید عددی باشد."
                ),
                ephemeral=True
            )
        except Exception as e:
            await inter.response.send_message(
                embed=Embeds.error(
                    "❌ خطا",
                    f"خطایی رخ داد: {str(e)}"
                ),
                ephemeral=True
            )
    
    @commands.slash_command(
        name="remove-premium",
        description="حذف اشتراک پریمیوم کاربر"
    )
    async def remove_premium(
        self,
        inter: ApplicationCommandInteraction,
        user_id: str = Option(
            name="user_id",
            description="آیدی کاربر",
            required=True
        )
    ):
        """Remove premium from a user"""
        # Check if user is an owner
        if str(inter.user.id) not in [str(owner_id) for owner_id in self.config.get('owner_ids', [])]:
            await inter.response.send_message(
                embed=Embeds.error(
                    "❌ خطا",
                    "شما دسترسی لازم برای استفاده از این دستور را ندارید."
                ),
                ephemeral=True
            )
            return
            
        try:
            # Try to convert user_id to int
            user_id = int(user_id)
            
            # Remove premium from user
            success = self.db.remove_premium_user(user_id)
            
            if success:
                # Fetch user object if possible
                user = self.bot.get_user(user_id)
                user_mention = f"<@{user_id}>" if not user else user.mention
                
                await inter.response.send_message(
                    embed=Embeds.success(
                        "✅ اشتراک پریمیوم حذف شد",
                        f"اشتراک پریمیوم کاربر {user_mention} با موفقیت حذف شد."
                    ),
                    ephemeral=True
                )
                
                # Try to notify the user
                if user:
                    try:
                        await user.send(
                            embed=Embeds.info(
                                "⚠️ اشتراک پریمیوم غیرفعال شد",
                                f"اشتراک پریمیوم شما غیرفعال شد!\n"
                                f"برای خرید دوباره اشتراک پریمیوم، به سرور ما بپیوندید:\n{self.premium_invite_link}"
                            )
                        )
                    except:
                        # Failed to DM user, just continue
                        pass
            else:
                await inter.response.send_message(
                    embed=Embeds.error(
                        "❌ خطا",
                        "کاربر مورد نظر اشتراک پریمیوم ندارد."
                    ),
                    ephemeral=True
                )
                
        except ValueError:
            await inter.response.send_message(
                embed=Embeds.error(
                    "❌ خطا",
                    "آیدی کاربر باید عددی باشد."
                ),
                ephemeral=True
            )
        except Exception as e:
            await inter.response.send_message(
                embed=Embeds.error(
                    "❌ خطا",
                    f"خطایی رخ داد: {str(e)}"
                ),
                ephemeral=True
            )
    
    @commands.slash_command(
        name="check-premium",
        description="بررسی وضعیت اشتراک پریمیوم"
    )
    async def check_premium(self, inter: ApplicationCommandInteraction):
        """Check premium status"""
        # Get premium status
        is_premium = self.db.is_premium_user(inter.user.id)
        
        if is_premium:
            expiry_date = self.db.get_premium_expiry(inter.user.id)
            embed = Embeds.premium_info(inter.user, expiry_date)
            
            # Get usage stats for informational purposes
            _, text_usage, text_limit = self.db.check_usage_limits(inter.user.id, "text")
            _, image_usage, image_limit = self.db.check_usage_limits(inter.user.id, "image")
            
            embed.add_field(
                name="💬 درخواست‌های متنی",
                value="نامحدود ♾️",
                inline=True
            )
            
            embed.add_field(
                name="🖼️ درخواست‌های تصویری",
                value="نامحدود ♾️",
                inline=True
            )
            
            await inter.response.send_message(
                embed=embed,
                ephemeral=True
            )
        else:
            embed = Embeds.premium_info(inter.user)
            
            # Add usage information
            _, text_usage, text_limit = self.db.check_usage_limits(inter.user.id, "text")
            _, image_usage, image_limit = self.db.check_usage_limits(inter.user.id, "image")
            
            embed.add_field(
                name="💬 درخواست‌های متنی",
                value=f"{text_usage}/{text_limit} امروز",
                inline=True
            )
            
            embed.add_field(
                name="🖼️ درخواست‌های تصویری",
                value=f"{image_usage}/{image_limit} امروز",
                inline=True
            )
            
            embed.add_field(
                name="✨ ارتقا به پریمیوم",
                value=f"برای خرید اشتراک پریمیوم و دسترسی نامحدود به تمام مدل‌ها، به سرور ما بپیوندید:\n{self.premium_invite_link}",
                inline=False
            )
            
            await inter.response.send_message(
                embed=embed,
                ephemeral=True
            )

def setup(bot):
    bot.add_cog(Premium(bot)) 