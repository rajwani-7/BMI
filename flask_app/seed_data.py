"""
Seed Sample Data for HealthCompanion
Populates realistic fitness data for testing and demonstration
"""

import sqlite3
from datetime import datetime, timedelta
import random


def seed_user_data(db_path, user_id):
    """
    Seed 30 days of sample fitness data for a user
    Includes: daily logs (water, workout) and BMI history
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"🌱 Seeding data for user {user_id}...")
    
    # Clear existing data for this user
    cursor.execute('DELETE FROM daily_logs WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM bmi_history WHERE user_id = ? AND date >= datetime("now", "-30 days")', (user_id,))
    
    today = datetime.now()
    
    # Generate 30 days of daily logs
    print("📝 Creating daily activity logs...")
    for i in range(30, 0, -1):
        date = today - timedelta(days=i)
        
        # Realistic water intake (4-10 glasses, trending upward)
        base_water = 5 + (30 - i) * 0.08  # Gradual increase
        water_intake = int(base_water + random.uniform(-1, 2))
        water_intake = max(3, min(10, water_intake))  # Clamp between 3-10
        
        # Workout done (60-70% consistency, better in recent days)
        workout_probability = 0.5 + (30 - i) * 0.008  # Improving consistency
        workout_done = 1 if random.random() < workout_probability else 0
        
        cursor.execute('''
            INSERT INTO daily_logs (user_id, water_intake, workout_done, date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, water_intake, workout_done, date.strftime('%Y-%m-%d %H:%M:%S')))
    
    # Generate BMI history (weight loss trend)
    print("⚖️ Creating BMI history...")
    
    # Get user's current profile
    cursor.execute('SELECT height, weight FROM health_profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    
    if profile:
        height_cm = profile[0]
        current_weight = profile[1]
        
        # Generate 30 data points showing gradual weight loss
        for i in range(30, 0, -1):
            date = today - timedelta(days=i)
            
            # Weight decreases gradually (realistic 0.1-0.15 kg per day loss = 3-4.5 kg per month)
            weight_loss = (30 - i) * 0.12 + random.uniform(-0.3, 0.3)
            weight = current_weight + weight_loss
            
            # Calculate BMI
            height_m = height_cm / 100
            bmi = weight / (height_m ** 2)
            
            cursor.execute('''
                INSERT INTO bmi_history (user_id, bmi, weight, height, date)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, round(bmi, 2), round(weight, 2), height_cm, date.strftime('%Y-%m-%d %H:%M:%S')))
    else:
        # Create sample BMI history even without profile
        print("⚠️ No profile found, using default values...")
        height_cm = 170
        start_weight = 75
        
        for i in range(30, 0, -1):
            date = today - timedelta(days=i)
            weight_loss = (30 - i) * 0.12 + random.uniform(-0.3, 0.3)
            weight = start_weight - weight_loss
            
            height_m = height_cm / 100
            bmi = weight / (height_m ** 2)
            
            cursor.execute('''
                INSERT INTO bmi_history (user_id, bmi, weight, height, date)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, round(bmi, 2), round(weight, 2), height_cm, date.strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM daily_logs WHERE user_id = ?', (user_id,))
    log_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM bmi_history WHERE user_id = ? AND date >= datetime("now", "-30 days")', (user_id,))
    bmi_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ Seeding complete!")
    print(f"   📊 Daily logs: {log_count}")
    print(f"   ⚖️ BMI records: {bmi_count}")
    
    return True


if __name__ == '__main__':
    # For testing
    import os
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'health_companion.db')
    if os.path.exists(db_path):
        # Seed for user ID 1
        seed_user_data(db_path, 1)
    else:
        print("❌ Database not found!")
