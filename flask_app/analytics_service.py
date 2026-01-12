"""
Analytics Service for HealthCompanion
Provides weekly fitness reports, trend analysis, and actionable insights
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class AnalyticsService:
    """Service for generating fitness analytics and insights"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_db(self):
        """Create database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_weekly_report(self, user_id: int) -> Dict:
        """
        Generate comprehensive weekly fitness report
        Returns data for charts and insight cards
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Calculate date range (last 7 days)
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        report = {
            'has_data': False,
            'weight_data': [],
            'bmi_data': [],
            'water_data': [],
            'workout_data': [],
            'insights': [],
            'stats': {}
        }
        
        # Fetch weight history (last 30 days for better trend visibility)
        cursor.execute('''
            SELECT weight, date 
            FROM bmi_history 
            WHERE user_id = ? AND date >= datetime('now', '-30 days')
            ORDER BY date ASC
        ''', (user_id,))
        weight_history = cursor.fetchall()
        
        if weight_history:
            report['has_data'] = True
            report['weight_data'] = [
                {'date': row['date'][:10], 'weight': round(row['weight'], 1)}
                for row in weight_history
            ]
            
            # Calculate weight change (weekly)
            weekly_weights = [row for row in weight_history 
                            if datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S') >= week_ago]
            
            if len(weekly_weights) >= 2:
                weight_change = weekly_weights[-1]['weight'] - weekly_weights[0]['weight']
                report['stats']['weight_change'] = round(weight_change, 2)
                
                # Generate weight insight
                if abs(weight_change) < 0.2:
                    report['insights'].append({
                        'icon': '📊',
                        'title': 'Weight Stable',
                        'message': 'Your weight remained stable this week.',
                        'type': 'neutral'
                    })
                elif weight_change < 0:
                    report['insights'].append({
                        'icon': '🎉',
                        'title': 'Weight Loss Progress',
                        'message': f'You lost {abs(weight_change):.1f} kg this week! Keep it up!',
                        'type': 'success'
                    })
                else:
                    report['insights'].append({
                        'icon': '⚠️',
                        'title': 'Weight Increased',
                        'message': f'Weight increased by {weight_change:.1f} kg. Review your diet plan.',
                        'type': 'warning'
                    })
        
        # Fetch BMI history (last 30 days)
        cursor.execute('''
            SELECT bmi, date 
            FROM bmi_history 
            WHERE user_id = ? AND date >= datetime('now', '-30 days')
            ORDER BY date ASC
        ''', (user_id,))
        bmi_history = cursor.fetchall()
        
        if bmi_history:
            report['bmi_data'] = [
                {'date': row['date'][:10], 'bmi': round(row['bmi'], 1)}
                for row in bmi_history
            ]
            
            # Calculate BMI trend
            if len(bmi_history) >= 2:
                bmi_change = bmi_history[-1]['bmi'] - bmi_history[0]['bmi']
                report['stats']['bmi_trend'] = round(bmi_change, 2)
                
                current_bmi = bmi_history[-1]['bmi']
                if current_bmi >= 30:
                    report['insights'].append({
                        'icon': '🚨',
                        'title': 'BMI Alert',
                        'message': 'Your BMI is in the obese range. Consult a healthcare professional.',
                        'type': 'danger'
                    })
                elif current_bmi >= 25:
                    report['insights'].append({
                        'icon': '⚖️',
                        'title': 'BMI Attention',
                        'message': 'BMI indicates overweight. Focus on balanced diet and exercise.',
                        'type': 'warning'
                    })
                elif 18.5 <= current_bmi < 25:
                    report['insights'].append({
                        'icon': '✅',
                        'title': 'Healthy BMI',
                        'message': 'Your BMI is in the healthy range. Great work!',
                        'type': 'success'
                    })
        
        # Fetch water intake data (last 7 days)
        cursor.execute('''
            SELECT water_intake, date 
            FROM daily_logs 
            WHERE user_id = ? AND date >= datetime('now', '-7 days')
            ORDER BY date ASC
        ''', (user_id,))
        water_logs = cursor.fetchall()
        
        if water_logs:
            report['water_data'] = [
                {'date': row['date'][:10], 'glasses': row['water_intake']}
                for row in water_logs
            ]
            
            # Calculate average water intake
            avg_water = sum(row['water_intake'] for row in water_logs) / len(water_logs)
            report['stats']['avg_water'] = round(avg_water, 1)
            
            # Generate water insight
            if avg_water >= 8:
                report['insights'].append({
                    'icon': '💧',
                    'title': 'Excellent Hydration',
                    'message': f'Average {avg_water:.0f} glasses/day. You\'re well hydrated!',
                    'type': 'success'
                })
            elif avg_water >= 6:
                report['insights'].append({
                    'icon': '💦',
                    'title': 'Good Hydration',
                    'message': f'Average {avg_water:.0f} glasses/day. Try to drink a bit more.',
                    'type': 'neutral'
                })
            else:
                report['insights'].append({
                    'icon': '🚰',
                    'title': 'Low Hydration',
                    'message': f'Only {avg_water:.0f} glasses/day. Increase water intake!',
                    'type': 'warning'
                })
        
        # Fetch workout data (last 7 days)
        cursor.execute('''
            SELECT workout_done, date 
            FROM daily_logs 
            WHERE user_id = ? AND date >= datetime('now', '-7 days')
            ORDER BY date ASC
        ''', (user_id,))
        workout_logs = cursor.fetchall()
        
        if workout_logs:
            workout_count = sum(1 for row in workout_logs if row['workout_done'] == 1)
            total_days = len(workout_logs)
            consistency = (workout_count / total_days) * 100 if total_days > 0 else 0
            
            report['stats']['workout_consistency'] = round(consistency, 0)
            report['stats']['workout_count'] = workout_count
            
            # Generate workout insight
            if consistency >= 80:
                report['insights'].append({
                    'icon': '💪',
                    'title': 'Workout Champion',
                    'message': f'{int(consistency)}% workout consistency. Amazing dedication!',
                    'type': 'success'
                })
            elif consistency >= 50:
                report['insights'].append({
                    'icon': '🏃',
                    'title': 'Good Effort',
                    'message': f'{int(consistency)}% consistency. Keep pushing!',
                    'type': 'neutral'
                })
            else:
                report['insights'].append({
                    'icon': '📉',
                    'title': 'Low Activity',
                    'message': f'Only {int(consistency)}% consistency. Try to exercise more regularly.',
                    'type': 'warning'
                })
        
        # Check for data availability
        if not report['has_data'] and not water_logs and not workout_logs:
            report['insights'].append({
                'icon': '📝',
                'title': 'Start Tracking',
                'message': 'No data available. Start logging your daily activities!',
                'type': 'info'
            })
        
        conn.close()
        return report
    
    def log_daily_activity(self, user_id: int, water_intake: int, workout_done: bool) -> bool:
        """
        Log daily activity (water intake and workout)
        Returns True if successful
        """
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            
            # Check if today's log exists
            cursor.execute('''
                SELECT id FROM daily_logs 
                WHERE user_id = ? AND date(date) = date('now')
            ''', (user_id,))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing log
                cursor.execute('''
                    UPDATE daily_logs 
                    SET water_intake = ?, workout_done = ?, date = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (water_intake, 1 if workout_done else 0, existing['id']))
            else:
                # Insert new log
                cursor.execute('''
                    INSERT INTO daily_logs (user_id, water_intake, workout_done)
                    VALUES (?, ?, ?)
                ''', (user_id, water_intake, 1 if workout_done else 0))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging daily activity: {e}")
            return False
    
    def get_health_streak(self, user_id: int) -> int:
        """
        Calculate consecutive days of healthy activity
        (workout done OR water intake >= 8)
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, workout_done, water_intake 
            FROM daily_logs 
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT 30
        ''', (user_id,))
        
        logs = cursor.fetchall()
        conn.close()
        
        streak = 0
        for log in logs:
            if log['workout_done'] == 1 or log['water_intake'] >= 8:
                streak += 1
            else:
                break
        
        return streak
