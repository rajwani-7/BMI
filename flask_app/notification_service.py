"""
Notification Service for HealthCompanion
Manages in-app notifications and automatic triggers
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class NotificationService:
    """Service for managing user notifications"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_db(self):
        """Create database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_notification(self, user_id: int, title: str, message: str, 
                          notification_type: str = 'info', action_url: Optional[str] = None) -> bool:
        """
        Create a new notification for a user
        Types: info, success, warning, danger, reminder
        Returns True if successful
        """
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, type, action_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, title, message, notification_type, action_url))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating notification: {e}")
            return False
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False, limit: int = 50) -> List[Dict]:
        """
        Get notifications for a user
        Returns list of notification dictionaries
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM notifications 
            WHERE user_id = ?
        '''
        
        if unread_only:
            query += ' AND is_read = 0'
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        
        cursor.execute(query, (user_id, limit))
        notifications = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return notifications
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for a user"""
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM notifications 
            WHERE user_id = ? AND is_read = 0
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] if result else 0
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """
        Mark a notification as read
        Returns True if successful
        """
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications 
                SET is_read = 1, read_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            ''', (notification_id, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False
    
    def mark_all_as_read(self, user_id: int) -> bool:
        """Mark all notifications as read for a user"""
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications 
                SET is_read = 1, read_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND is_read = 0
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking all notifications as read: {e}")
            return False
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification"""
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM notifications 
                WHERE id = ? AND user_id = ?
            ''', (notification_id, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting notification: {e}")
            return False
    
    # ===== AUTOMATIC NOTIFICATION TRIGGERS =====
    
    def check_missed_workouts(self, user_id: int) -> None:
        """
        Check if user missed workouts and send notification
        Checks last 2 days
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM daily_logs 
            WHERE user_id = ? 
            AND date >= datetime('now', '-2 days')
            AND workout_done = 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        workout_count = result['count'] if result else 0
        
        if workout_count == 0:
            # Check if notification already sent today
            cursor.execute('''
                SELECT id FROM notifications 
                WHERE user_id = ? 
                AND title = 'Missed Workouts'
                AND date(created_at) = date('now')
            ''', (user_id,))
            
            if not cursor.fetchone():
                self.create_notification(
                    user_id,
                    'Missed Workouts',
                    '⚠️ You haven\'t logged any workouts in the last 2 days. Stay active!',
                    'warning',
                    '/dashboard'
                )
        
        conn.close()
    
    def check_low_water_intake(self, user_id: int) -> None:
        """
        Check if water intake is low and send notification
        Checks today's log
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT water_intake FROM daily_logs 
            WHERE user_id = ? 
            AND date(date) = date('now')
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if result and result['water_intake'] < 6:
            # Check if notification already sent today
            cursor.execute('''
                SELECT id FROM notifications 
                WHERE user_id = ? 
                AND title = 'Low Water Intake'
                AND date(created_at) = date('now')
            ''', (user_id,))
            
            if not cursor.fetchone():
                self.create_notification(
                    user_id,
                    'Low Water Intake',
                    f'💧 You\'ve only had {result["water_intake"]} glasses today. Drink more water!',
                    'warning',
                    '/dashboard'
                )
        
        conn.close()
    
    def check_bmi_increase(self, user_id: int) -> None:
        """
        Check if BMI increased significantly and send warning
        Compares last two BMI entries
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bmi, date FROM bmi_history 
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT 2
        ''', (user_id,))
        
        results = cursor.fetchall()
        
        if len(results) == 2:
            latest_bmi = results[0]['bmi']
            previous_bmi = results[1]['bmi']
            bmi_increase = latest_bmi - previous_bmi
            
            if bmi_increase >= 1.0:  # BMI increased by 1 or more
                # Check if notification already sent for this update
                cursor.execute('''
                    SELECT id FROM notifications 
                    WHERE user_id = ? 
                    AND title = 'BMI Increase Alert'
                    AND created_at >= ?
                ''', (user_id, results[0]['date']))
                
                if not cursor.fetchone():
                    self.create_notification(
                        user_id,
                        'BMI Increase Alert',
                        f'📈 Your BMI increased by {bmi_increase:.1f} points. Review your health plan.',
                        'danger',
                        '/profile'
                    )
        
        conn.close()
    
    def check_streak_break(self, user_id: int) -> None:
        """
        Check if user's health streak was broken
        """
        from analytics_service import AnalyticsService
        
        analytics = AnalyticsService(self.db_path)
        streak = analytics.get_health_streak(user_id)
        
        if streak == 0:
            conn = self.get_db()
            cursor = conn.cursor()
            
            # Check if notification already sent today
            cursor.execute('''
                SELECT id FROM notifications 
                WHERE user_id = ? 
                AND title = 'Streak Broken'
                AND date(created_at) = date('now')
            ''', (user_id,))
            
            if not cursor.fetchone():
                self.create_notification(
                    user_id,
                    'Streak Broken',
                    '💔 Your health streak ended. Start fresh today!',
                    'info',
                    '/dashboard'
                )
            
            conn.close()
    
    def send_achievement_notification(self, user_id: int, achievement: str) -> None:
        """Send achievement/milestone notification"""
        messages = {
            'first_log': ('🎉 First Step!', 'You logged your first daily activity. Keep going!'),
            'week_streak': ('🔥 Week Streak!', 'You maintained a 7-day health streak. Amazing!'),
            'month_streak': ('🏆 Month Champion!', 'Incredible! You have a 30-day health streak!'),
            'weight_goal': ('🎯 Goal Achieved!', 'Congratulations! You reached your weight goal!'),
        }
        
        if achievement in messages:
            title, message = messages[achievement]
            self.create_notification(user_id, title, message, 'success', '/analytics')
    
    def trigger_all_checks(self, user_id: int) -> None:
        """
        Run all automatic notification checks for a user
        Called periodically by scheduler
        """
        self.check_missed_workouts(user_id)
        self.check_low_water_intake(user_id)
        self.check_bmi_increase(user_id)
        self.check_streak_break(user_id)
