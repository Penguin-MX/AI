import disnake
import datetime

# Red theme color for embeds (Persian Red)
RED_COLOR = 0xE60000 

class Embeds:
    @staticmethod
    def error(title, description):
        """Create an error embed"""
        embed = disnake.Embed(
            title=title,
            description=description,
            color=RED_COLOR,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="Quick AI", icon_url="https://i.imgur.com/Px7h4a1.png")
        return embed
    
    @staticmethod
    def success(title, description):
        """Create a success embed"""
        embed = disnake.Embed(
            title=title,
            description=description,
            color=RED_COLOR,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="Quick AI", icon_url="https://i.imgur.com/Px7h4a1.png")
        return embed
    
    @staticmethod
    def info(title, description):
        """Create an info embed"""
        embed = disnake.Embed(
            title=title,
            description=description,
            color=RED_COLOR,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="Quick AI", icon_url="https://i.imgur.com/Px7h4a1.png")
        return embed
    
    @staticmethod
    def settings():
        """Create a settings embed"""
        embed = disnake.Embed(
            title="🛠️ تنظیمات Quick AI",
            description="لطفاً مدل مورد نظر خود را از منوهای زیر انتخاب کنید",
            color=RED_COLOR,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="📝 مدل‌های متن", value="برای انتخاب مدل متن استفاده کنید", inline=False)
        embed.add_field(name="🤖 عامل‌ها", value="برای انتخاب عامل هوش مصنوعی استفاده کنید", inline=False)
        embed.add_field(name="🖼️ مدل‌های تولید تصویر", value="برای انتخاب مدل تولید تصویر استفاده کنید", inline=False)
        embed.set_footer(text="Quick AI", icon_url="https://i.imgur.com/Px7h4a1.png")
        return embed
    
    @staticmethod
    def premium_info(user, expiry_date=None):
        """Create a premium status embed"""
        if expiry_date:
            # Check if unlimited
            if expiry_date == "Unlimited":
                embed = disnake.Embed(
                    title="✨ وضعیت اشتراک پریمیوم",
                    description=f"**{user.mention}** شما دارای اشتراک پریمیوم نامحدود هستید!",
                    color=RED_COLOR,
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="⏱️ تاریخ انقضا", value="```نامحدود ♾️```", inline=False)
            else:
                # Format expiry date to Persian style
                formatted_date = expiry_date.strftime("%Y/%m/%d %H:%M:%S")
                
                embed = disnake.Embed(
                    title="✨ وضعیت اشتراک پریمیوم",
                    description=f"**{user.mention}** شما دارای اشتراک پریمیوم هستید!",
                    color=RED_COLOR,
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="⏱️ تاریخ انقضا", value=f"```{formatted_date}```", inline=False)
                
                # Calculate days remaining
                days_remaining = (expiry_date - datetime.datetime.now()).days
                if days_remaining > 365:
                    years = days_remaining // 365
                    remaining_text = f"{years} سال"
                elif days_remaining > 30:
                    months = days_remaining // 30
                    remaining_text = f"{months} ماه"
                else:
                    remaining_text = f"{days_remaining} روز"
                    
                embed.add_field(name="⌛ زمان باقی‌مانده", value=f"```{remaining_text}```", inline=False)
        else:
            embed = disnake.Embed(
                title="❌ وضعیت اشتراک پریمیوم",
                description=f"**{user.mention}** شما اکانت پریمیوم ندارید!",
                color=RED_COLOR,
                timestamp=datetime.datetime.now()
            )
            
            # Add premium benefits
            benefits = [
                "✅ دسترسی به تمام مدل‌های هوش مصنوعی",
                "✅ بدون محدودیت تعداد درخواست‌های روزانه",
                "✅ کیفیت بالاتر تصاویر تولیدی",
                "✅ اولویت در پردازش درخواست‌ها"
            ]
            
            benefits_text = "\n".join(benefits)
            embed.add_field(name="✨ مزایای پریمیوم", value=benefits_text, inline=False)
            embed.add_field(name="💡 نحوه خرید اشتراک پریمیوم", value="برای خرید اشتراک پریمیوم به سرور ما بپیوندید:\nhttps://discord.gg/bQc7vw328d", inline=False)
        
        embed.set_footer(text="Quick AI", icon_url="https://i.imgur.com/Px7h4a1.png")
        return embed
    
    @staticmethod
    def response(content, user):
        """Create a response embed for AI responses"""
        embed = disnake.Embed(
            description=content,
            color=RED_COLOR,
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=f"پاسخ به {user.display_name}", icon_url=user.display_avatar.url)
        embed.set_footer(text="Quick AI", icon_url="https://i.imgur.com/Px7h4a1.png")
        return embed
    
    @staticmethod
    def image_response(prompt, image_url, user):
        """Create an image response embed"""
        embed = disnake.Embed(
            title="🖼️ تصویر تولید شده",
            description=f"**پرامپت:** {prompt}",
            color=RED_COLOR,
            timestamp=datetime.datetime.now()
        )
        embed.set_image(url=image_url)
        embed.set_author(name=f"درخواست {user.display_name}", icon_url=user.display_avatar.url)
        embed.set_footer(text="Quick AI", icon_url="https://i.imgur.com/Px7h4a1.png")
        return embed 