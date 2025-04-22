import sqlite3
from datetime import datetime, timedelta
import json
import os

class Database:
    def __init__(self, db_path='data/quickai.db'):
        self.db_path = db_path
        
        # Define usage limits
        self.FREE_DAILY_TEXT_LIMIT = 50
        self.FREE_DAILY_IMAGE_LIMIT = 15
        
        # Ensure the database exists
        self._connect()
        
        # Daily limits for free users
        self.daily_limits = {
            "text": 50,  # 50 text requests per day
            "image": 15  # 15 image requests per day
        }
        
        # Premium durations in days
        self.premium_durations = {
            "1d": 1,             # 1 day
            "7d": 7,             # 7 days (1 week)
            "1m": 30,            # 1 month (30 days)
            "3m": 90,            # 3 months (90 days)
            "1y": 365,           # 1 year (365 days)
            "3y": 1095,          # 3 years (1095 days)
            "unlimited": -1      # Unlimited (-1 means no expiration)
        }
    
    def _connect(self):
        """Create a connection to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
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
        
        # New table for tracking daily usage
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
    
    def add_premium_user(self, user_id, days=30):
        """Add a user to the premium users list"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate expiration date
        if days == 0:  # Unlimited
            expires_at = "unlimited"
        else:
            expires_at = (datetime.now() + timedelta(days=days)).isoformat()
        
        # Insert or update the user
        cursor.execute(
            "INSERT OR REPLACE INTO premium_users (user_id, expires_at) VALUES (?, ?)",
            (user_id, expires_at)
        )
        
        conn.commit()
        conn.close()
        
        return expires_at
    
    def remove_premium_user(self, user_id):
        """Remove a user from the premium users list"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM premium_users WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def is_premium_user(self, user_id):
        """Check if a user is premium and the premium status is still valid"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT expires_at FROM premium_users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            expires_at = result[0]
            if expires_at == "unlimited":
                return True
            return datetime.fromisoformat(expires_at) > datetime.now()
        
        return False
    
    def get_premium_expiry(self, user_id):
        """Get the expiry date of a premium user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT expires_at FROM premium_users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            if result[0] == "unlimited":
                return "Unlimited"
            return datetime.fromisoformat(result[0])
        
        return None
    
    def get_premium_duration_text(self, user_id):
        """Get formatted text about premium duration"""
        expiry = self.get_premium_expiry(user_id)
        
        if not expiry:
            return "No premium"
        
        if expiry == "Unlimited":
            return "Unlimited premium"
        
        days_remaining = (expiry - datetime.now()).days
        
        if days_remaining > 365:
            years = days_remaining // 365
            return f"{years} year{'s' if years > 1 else ''}"
        elif days_remaining > 30:
            months = days_remaining // 30
            return f"{months} month{'s' if months > 1 else ''}"
        else:
            return f"{days_remaining} day{'s' if days_remaining != 1 else ''}"
    
    def increment_usage(self, user_id, usage_type):
        """Increment the usage counter for a user"""
        if usage_type not in ["text", "image"]:
            return False
        
        # Get today's date in YYYY-MM-DD format
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if there's an entry for today
        cursor.execute(
            "SELECT text_requests, image_requests FROM usage_tracking WHERE user_id = ? AND date = ?",
            (user_id, today)
        )
        result = cursor.fetchone()
        
        if result:
            # Update existing entry
            text_requests, image_requests = result
            
            if usage_type == "text":
                text_requests += 1
            else:  # image
                image_requests += 1
                
            cursor.execute(
                "UPDATE usage_tracking SET text_requests = ?, image_requests = ? WHERE user_id = ? AND date = ?",
                (text_requests, image_requests, user_id, today)
            )
        else:
            # Create new entry
            text_requests = 1 if usage_type == "text" else 0
            image_requests = 1 if usage_type == "image" else 0
            
            cursor.execute(
                "INSERT INTO usage_tracking (user_id, date, text_requests, image_requests) VALUES (?, ?, ?, ?)",
                (user_id, today, text_requests, image_requests)
            )
        
        conn.commit()
        conn.close()
        
        return True
    
    def check_usage_limits(self, user_id, usage_type):
        """Check if user has reached daily usage limits"""
        # Premium users have unlimited usage
        if self.is_premium_user(user_id):
            return False, 0, float('inf')
            
        # Get today's date in format YYYY-MM-DD
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Check if there's an entry for today
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT count FROM usage_tracking WHERE user_id = ? AND usage_type = ? AND date = ?",
            (user_id, usage_type, today)
        )
        result = cursor.fetchone()
        
        # Get the limit for this usage type
        limit = self.daily_limits.get(usage_type, 10)  # Default to 10 if not specified
        
        conn.close()
        
        if result:
            current_usage = result[0]
            # Check if limit is reached
            return current_usage >= limit, current_usage, limit
        else:
            # No usage yet today
            return False, 0, limit
    
    def save_user_settings(self, user_id, text_model=None, image_model=None, agent=None):
        """Save user settings to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current settings
        cursor.execute(
            "SELECT text_model, image_model, agent FROM user_settings WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        
        if result:
            current_text_model, current_image_model, current_agent = result
            
            # Update with new values, or keep current ones if None
            text_model = text_model if text_model is not None else current_text_model
            image_model = image_model if image_model is not None else current_image_model
            agent = agent if agent is not None else current_agent
            
            cursor.execute(
                "UPDATE user_settings SET text_model = ?, image_model = ?, agent = ? WHERE user_id = ?",
                (text_model, image_model, agent, user_id)
            )
        else:
            # Use default values for None
            if text_model is None:
                text_model = "openai"
            if image_model is None:
                image_model = "flux"
            if agent is None:
                agent = "agent-1"
                
            cursor.execute(
                "INSERT INTO user_settings (user_id, text_model, image_model, agent) VALUES (?, ?, ?, ?)",
                (user_id, text_model, image_model, agent)
            )
        
        conn.commit()
        conn.close()
        
        return {
            "text_model": text_model,
            "image_model": image_model,
            "agent": agent
        }
    
    def get_user_settings(self, user_id):
        """Get user settings from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT text_model, image_model, agent FROM user_settings WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                "text_model": result[0],
                "image_model": result[1],
                "agent": result[2]
            }
        else:
            # Return default settings
            return {
                "text_model": "openai",
                "image_model": "flux",
                "agent": "agent-1"
            }
    
    def track_usage(self, user_id, usage_type):
        """Track user's usage"""
        # Get today's date in format YYYY-MM-DD
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Check if there's an entry for today
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT count FROM usage_tracking WHERE user_id = ? AND usage_type = ? AND date = ?",
            (user_id, usage_type, today)
        )
        result = cursor.fetchone()
        
        if result:
            # Update existing entry
            cursor.execute(
                "UPDATE usage_tracking SET count = count + 1 WHERE user_id = ? AND usage_type = ? AND date = ?",
                (user_id, usage_type, today)
            )
        else:
            # Create new entry
            cursor.execute(
                "INSERT INTO usage_tracking (user_id, usage_type, date, count) VALUES (?, ?, ?, 1)",
                (user_id, usage_type, today)
            )
        
        conn.commit()
        conn.close()
    
    def get_daily_usage(self, user_id, usage_type):
        """Get user's usage for today"""
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT count FROM usage_tracking WHERE user_id = ? AND usage_type = ? AND date = ?",
            (user_id, usage_type, today)
        )
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0
    
    def check_usage_limit(self, user_id, usage_type):
        """Check if a user has reached their daily usage limit"""
        # First check if the user is premium
        if self.is_premium_user(user_id):
            return False  # Premium users have no limits
        
        # Get current usage
        current_usage = self.get_daily_usage(user_id, usage_type)
        
        # Define limits for free users
        limits = {
            "text": 50,
            "image": 15
        }
        
        # Check if the user has reached the limit
        if usage_type in limits and current_usage >= limits[usage_type]:
            return True
            
        return False 