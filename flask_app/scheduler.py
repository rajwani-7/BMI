"""
Scheduler for HealthCompanion
Handles automated reminders and periodic notification checks using APScheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import sqlite3


class ReminderScheduler:
    """Scheduler for automated reminders and notifications"""
    
    def __init__(self, db_path: str, app):
        self.db_path = db_path
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.notification_service = None
    
    def get_db(self):
        """Create database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def set_notification_service(self, notification_service):
        """Set notification service instance"""
        self.notification_service = notification_service
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            # Add scheduled jobs
            self._add_scheduled_jobs()
            self.scheduler.start()
            print("✅ Reminder scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("🛑 Reminder scheduler stopped")
    
    def _add_scheduled_jobs(self):
        """Add all scheduled jobs"""
        
        # Water reminder - every 2 hours during waking hours (8 AM - 10 PM)
        self.scheduler.add_job(
            func=self._send_water_reminders,
            trigger=CronTrigger(hour='8-22/2'),  # Every 2 hours from 8 AM to 10 PM
            id='water_reminder',
            name='Water Intake Reminder',
            replace_existing=True
        )
        
        # Workout reminder - daily at 6 PM
        self.scheduler.add_job(
            func=self._send_workout_reminders,
            trigger=CronTrigger(hour=18, minute=0),  # 6:00 PM daily
            id='workout_reminder',
            name='Daily Workout Reminder',
            replace_existing=True
        )
        
        # Check for automated notifications - every 3 hours
        self.scheduler.add_job(
            func=self._check_automated_notifications,
            trigger=IntervalTrigger(hours=3),
            id='auto_notifications',
            name='Automatic Notification Checks',
            replace_existing=True
        )
        
        # Meal reminders will be scheduled dynamically based on user settings
        self.scheduler.add_job(
            func=self._send_meal_reminders,
            trigger=CronTrigger(hour='*', minute='*/30'),  # Check every 30 minutes
            id='meal_reminder_check',
            name='Meal Reminder Check',
            replace_existing=True
        )
    
    def _send_water_reminders(self):
        """Send water intake reminders to users with reminders enabled"""
        with self.app.app_context():
            if not self.notification_service:
                return
            
            conn = self.get_db()
            cursor = conn.cursor()
            
            # Get users with water reminders enabled
            cursor.execute('''
                SELECT user_id FROM reminder_settings 
                WHERE water_reminder = 1
            ''')
            
            users = cursor.fetchall()
            conn.close()
            
            for user in users:
                user_id = user['user_id']
                
                # Check if already sent reminder in last 2 hours
                conn = self.get_db()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id FROM notifications 
                    WHERE user_id = ? 
                    AND title = 'Water Reminder'
                    AND created_at >= datetime('now', '-2 hours')
                ''', (user_id,))
                
                recent_reminder = cursor.fetchone()
                conn.close()
                
                if not recent_reminder:
                    self.notification_service.create_notification(
                        user_id,
                        'Water Reminder',
                        '💧 Time to drink water! Stay hydrated throughout the day.',
                        'reminder',
                        '/dashboard'
                    )
            
            print(f"💧 Water reminders sent to {len(users)} users")
    
    def _send_workout_reminders(self):
        """Send workout reminders to users"""
        with self.app.app_context():
            if not self.notification_service:
                return
            
            conn = self.get_db()
            cursor = conn.cursor()
            
            # Get users with workout reminders enabled
            cursor.execute('''
                SELECT user_id FROM reminder_settings 
                WHERE workout_reminder = 1
            ''')
            
            users = cursor.fetchall()
            conn.close()
            
            for user in users:
                user_id = user['user_id']
                
                # Check if workout already done today
                conn = self.get_db()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT workout_done FROM daily_logs 
                    WHERE user_id = ? 
                    AND date(date) = date('now')
                ''', (user_id,))
                
                log = cursor.fetchone()
                
                # Only send reminder if workout not done
                if not log or log['workout_done'] == 0:
                    # Check if reminder already sent today
                    cursor.execute('''
                        SELECT id FROM notifications 
                        WHERE user_id = ? 
                        AND title = 'Workout Reminder'
                        AND date(created_at) = date('now')
                    ''', (user_id,))
                    
                    if not cursor.fetchone():
                        self.notification_service.create_notification(
                            user_id,
                            'Workout Reminder',
                            '💪 Time for your daily workout! Get moving and stay fit.',
                            'reminder',
                            '/dashboard'
                        )
                
                conn.close()
            
            print(f"💪 Workout reminders sent to {len(users)} users")
    
    def _send_meal_reminders(self):
        """Send meal reminders based on user-configured times"""
        with self.app.app_context():
            if not self.notification_service:
                return
            
            current_time = datetime.now().strftime('%H:%M')
            current_hour = datetime.now().hour
            current_minute = datetime.now().minute
            
            conn = self.get_db()
            cursor = conn.cursor()
            
            # Get users with meal notifications enabled
            cursor.execute('''
                SELECT user_id, breakfast_time, lunch_time, snack_time, dinner_time 
                FROM notification_settings 
                WHERE enabled = 1
            ''')
            
            users = cursor.fetchall()
            conn.close()
            
            meal_types = {
                'breakfast_time': ('Breakfast Time', '🌅 Good morning! Time for a healthy breakfast.'),
                'lunch_time': ('Lunch Time', '🥗 It\'s lunch time! Enjoy a nutritious meal.'),
                'snack_time': ('Snack Time', '🥤 Snack time! Have something healthy.'),
                'dinner_time': ('Dinner Time', '🍽️ Dinner is ready! Time for your evening meal.'),
            }
            
            for user in users:
                user_id = user['user_id']
                
                for meal_field, (title, message) in meal_types.items():
                    meal_time = user[meal_field]
                    
                    if meal_time:
                        # Parse meal time
                        meal_hour, meal_minute = map(int, meal_time.split(':'))
                        
                        # Check if current time matches meal time (within 30-minute window)
                        if meal_hour == current_hour and abs(meal_minute - current_minute) <= 15:
                            # Check if notification already sent for this meal today
                            conn = self.get_db()
                            cursor = conn.cursor()
                            cursor.execute('''
                                SELECT id FROM notifications 
                                WHERE user_id = ? 
                                AND title = ?
                                AND date(created_at) = date('now')
                            ''', (user_id, title))
                            
                            if not cursor.fetchone():
                                self.notification_service.create_notification(
                                    user_id,
                                    title,
                                    message,
                                    'reminder',
                                    '/diet'
                                )
                            
                            conn.close()
    
    def _check_automated_notifications(self):
        """Run automated notification checks for all active users"""
        with self.app.app_context():
            if not self.notification_service:
                return
            
            conn = self.get_db()
            cursor = conn.cursor()
            
            # Get all users (you can add filters for active users)
            cursor.execute('SELECT id FROM users')
            users = cursor.fetchall()
            conn.close()
            
            for user in users:
                user_id = user['id']
                try:
                    self.notification_service.trigger_all_checks(user_id)
                except Exception as e:
                    print(f"Error checking notifications for user {user_id}: {e}")
            
            print(f"✅ Automated notification checks completed for {len(users)} users")
    
    def enable_user_reminders(self, user_id: int, water: bool = True, 
                            workout: bool = True) -> bool:
        """
        Enable/disable reminders for a specific user
        Returns True if successful
        """
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            
            # Check if settings exist
            cursor.execute('SELECT id FROM reminder_settings WHERE user_id = ?', (user_id,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE reminder_settings 
                    SET water_reminder = ?, workout_reminder = ?
                    WHERE user_id = ?
                ''', (1 if water else 0, 1 if workout else 0, user_id))
            else:
                cursor.execute('''
                    INSERT INTO reminder_settings (user_id, water_reminder, workout_reminder)
                    VALUES (?, ?, ?)
                ''', (user_id, 1 if water else 0, 1 if workout else 0))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error enabling user reminders: {e}")
            return False
