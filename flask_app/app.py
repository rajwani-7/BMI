from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from datetime import datetime, timedelta
import json
import os
import atexit

# Import service modules
from analytics_service import AnalyticsService
from notification_service import NotificationService
from scheduler import ReminderScheduler

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Set database path to work in both development and production
if os.path.exists('health_companion.db'):
    app.config['DATABASE'] = 'health_companion.db'
else:
    app.config['DATABASE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'health_companion.db')

# Initialize services
analytics_service = AnalyticsService(app.config['DATABASE'])
notification_service = NotificationService(app.config['DATABASE'])
scheduler = ReminderScheduler(app.config['DATABASE'], app)
scheduler.set_notification_service(notification_service)

# Error handler for 500 errors
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Internal Server Error: {error}')
    return render_template('index.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f'Unhandled exception: {str(e)}')
    return f"An error occurred: {str(e)}", 500

# ===== DATABASE FUNCTIONS =====

def get_db():
    """Create database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            fullname TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Health profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            age INTEGER,
            gender TEXT,
            height REAL,
            weight REAL,
            activity_level TEXT,
            sleep_hours REAL,
            water_intake INTEGER,
            diet_preference TEXT,
            goal TEXT,
            medical_conditions TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # BMI history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bmi_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bmi REAL NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Health score history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_score_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Notification settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            enabled BOOLEAN DEFAULT 0,
            breakfast_time TEXT,
            lunch_time TEXT,
            snack_time TEXT,
            dinner_time TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Daily logs table - for tracking water intake and workouts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            water_intake INTEGER DEFAULT 0,
            workout_done BOOLEAN DEFAULT 0,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Notifications table - stores in-app notifications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            action_url TEXT,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Reminder settings table - for water and workout reminders
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminder_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            water_reminder BOOLEAN DEFAULT 1,
            workout_reminder BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# ===== AUTHENTICATION DECORATOR =====

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ===== HEALTH CALCULATION FUNCTIONS =====

def calculate_bmi(weight, height):
    """Calculate BMI (weight in kg, height in cm)"""
    height_m = height / 100
    return weight / (height_m ** 2)

def get_bmi_category(bmi):
    """Get BMI category and status"""
    if bmi < 18.5:
        return {'category': 'Underweight', 'status': 'Below ideal weight', 'color': 'cyan'}
    elif bmi < 25:
        return {'category': 'Normal', 'status': 'Healthy weight', 'color': 'green'}
    elif bmi < 30:
        return {'category': 'Overweight', 'status': 'Above ideal weight', 'color': 'orange'}
    else:
        return {'category': 'Obese', 'status': 'Significantly above ideal weight', 'color': 'red'}

def calculate_health_score(profile):
    """Calculate health score (0-100)"""
    score = 50
    
    # BMI contribution (30%)
    bmi = calculate_bmi(profile['weight'], profile['height'])
    if 18.5 <= bmi < 25:
        score += 30
    elif 25 <= bmi < 30:
        score += 15
    elif bmi >= 30:
        score += 0
    else:
        score += 10
    
    # Activity level (25%)
    activity_scores = {'Low': 5, 'Medium': 20, 'High': 25}
    score += activity_scores.get(profile['activity_level'], 0)
    
    # Sleep hours (20%)
    sleep = profile['sleep_hours']
    if 7 <= sleep <= 9:
        score += 20
    elif (6 <= sleep < 7) or (9 < sleep <= 10):
        score += 12
    elif (5 <= sleep < 6) or (10 < sleep <= 11):
        score += 5
    
    # Water intake (15%)
    water = profile['water_intake']
    if water >= 8:
        score += 15
    elif water >= 6:
        score += 10
    elif water >= 4:
        score += 5
    
    # Medical conditions penalty
    conditions_str = profile['medical_conditions'] if profile['medical_conditions'] else '[]'
    conditions = json.loads(conditions_str)
    score -= len(conditions) * 5
    
    return max(0, min(100, score))

def get_health_status(score):
    """Get health status based on score"""
    if score >= 80:
        return {'status': 'Excellent', 'message': 'Keep it up! Your health is great.'}
    elif score >= 60:
        return {'status': 'Good', 'message': 'Good progress! Can improve further.'}
    elif score >= 40:
        return {'status': 'Fair', 'message': 'You need to focus on your health.'}
    else:
        return {'status': 'Poor', 'message': 'Urgent improvements needed. Consult a health professional.'}

# ===== ROUTES =====

@app.route('/')
def index():
    """Landing page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([fullname, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('register.html')
        
        # Check if user exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            flash('Email already registered', 'error')
            conn.close()
            return render_template('register.html')
        
        # Create user
        hashed_password = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (email, fullname, password) VALUES (?, ?, ?)',
            (email, fullname, hashed_password)
        )
        conn.commit()
        conn.close()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            if check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['fullname'] = user['fullname']
                session['email'] = user['email']
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password. Please check your password and try again.', 'error')
                return render_template('login.html')
        else:
            flash('Email not found. Please check your email or sign up.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user_id = session['user_id']
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get health profile
    cursor.execute('SELECT * FROM health_profiles WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
    profile = cursor.fetchone()
    
    dashboard_data = {}
    
    if profile:
        # Calculate BMI and health score
        bmi = calculate_bmi(profile['weight'], profile['height'])
        bmi_info = get_bmi_category(bmi)
        health_score = calculate_health_score(profile)
        status_info = get_health_status(health_score)
        
        dashboard_data = {
            'profile': dict(profile),
            'bmi': round(bmi, 1),
            'bmi_info': bmi_info,
            'health_score': health_score,
            'status_info': status_info
        }
    
    conn.close()
    
    return render_template('dashboard.html', data=dashboard_data, fullname=session['fullname'])

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Health profile management"""
    user_id = session['user_id']
    
    if request.method == 'POST':
        # Get form data
        age = request.form.get('age')
        gender = request.form.get('gender')
        height = float(request.form.get('height'))
        weight = float(request.form.get('weight'))
        activity_level = request.form.get('activity_level')
        sleep_hours = float(request.form.get('sleep_hours'))
        water_intake = int(request.form.get('water_intake'))
        diet_preference = request.form.get('diet_preference')
        goal = request.form.get('goal')
        
        # Get medical conditions
        conditions = request.form.getlist('conditions')
        conditions_json = json.dumps(conditions)
        
        # Validation
        if height < 100 or height > 250:
            flash('Height must be between 100cm and 250cm', 'error')
            return redirect(url_for('profile'))
        
        if weight < 20 or weight > 300:
            flash('Weight must be between 20kg and 300kg', 'error')
            return redirect(url_for('profile'))
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Insert or update profile
        cursor.execute('SELECT id FROM health_profiles WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE health_profiles 
                SET age=?, gender=?, height=?, weight=?, activity_level=?, 
                    sleep_hours=?, water_intake=?, diet_preference=?, goal=?, 
                    medical_conditions=?, updated_at=CURRENT_TIMESTAMP
                WHERE user_id=?
            ''', (age, gender, height, weight, activity_level, sleep_hours, 
                  water_intake, diet_preference, goal, conditions_json, user_id))
        else:
            cursor.execute('''
                INSERT INTO health_profiles 
                (user_id, age, gender, height, weight, activity_level, sleep_hours, 
                 water_intake, diet_preference, goal, medical_conditions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, age, gender, height, weight, activity_level, sleep_hours,
                  water_intake, diet_preference, goal, conditions_json))
        
        # Record BMI history
        bmi = calculate_bmi(weight, height)
        cursor.execute(
            'INSERT INTO bmi_history (user_id, bmi, weight, height) VALUES (?, ?, ?, ?)',
            (user_id, bmi, weight, height)
        )
        
        # Record health score
        cursor.execute('SELECT * FROM health_profiles WHERE user_id = ?', (user_id,))
        profile = cursor.fetchone()
        health_score = calculate_health_score(profile)
        cursor.execute(
            'INSERT INTO health_score_history (user_id, score) VALUES (?, ?)',
            (user_id, health_score)
        )
        
        conn.commit()
        conn.close()
        
        flash('Health profile saved successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # GET request - load existing profile
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM health_profiles WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
    profile = cursor.fetchone()
    conn.close()
    
    profile_data = dict(profile) if profile else {}
    if profile_data and profile_data.get('medical_conditions'):
        profile_data['medical_conditions'] = json.loads(profile_data.get('medical_conditions', '[]'))
    
    return render_template('profile.html', profile=profile_data)

@app.route('/diet')
@login_required
def diet():
    """Diet recommendations"""
    user_id = session['user_id']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM health_profiles WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
    profile = cursor.fetchone() 
    conn.close()
    
    if not profile:
        flash('Please set up your health profile first', 'error')
        return redirect(url_for('profile'))
    
    try:
        from diet_recommender import get_diet_plan
    except ImportError:
        try:
            from flask_app.diet_recommender import get_diet_plan
        except ImportError:
            # Fallback to relative import
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from diet_recommender import get_diet_plan
    
    diet_plan = get_diet_plan(dict(profile))
    
    return render_template('diet.html', diet=diet_plan, profile=dict(profile))

@app.route('/analytics')
@login_required
def analytics():
    """
    Analytics and progress tracking - Weekly Fitness Report
    Shows real insights with charts and data-driven recommendations
    """
    user_id = session['user_id']
    
    # Get weekly fitness report from analytics service
    report = analytics_service.get_weekly_report(user_id)
    
    return render_template('analytics.html', report=report)

@app.route('/notifications', methods=['GET'])
@login_required
def notifications():
    """
    Notification center - displays all notifications with mark as read functionality
    """
    user_id = session['user_id']
    
    # Get all notifications
    all_notifications = notification_service.get_user_notifications(user_id, unread_only=False, limit=50)
    unread_count = notification_service.get_unread_count(user_id)
    
    # Get reminder settings
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM reminder_settings WHERE user_id = ?', (user_id,))
    reminder_row = cursor.fetchone()
    reminder_settings = dict(reminder_row) if reminder_row else {
        'water_reminder': False,
        'workout_reminder': False
    }
    
    # Get meal notification settings
    cursor.execute('SELECT * FROM notification_settings WHERE user_id = ?', (user_id,))
    meal_row = cursor.fetchone()
    meal_settings = dict(meal_row) if meal_row else {
        'enabled': False,
        'breakfast_time': '07:00',
        'lunch_time': '13:00',
        'snack_time': '16:00',
        'dinner_time': '19:00'
    }
    
    conn.close()
    
    return render_template('notifications.html', 
                         notifications=all_notifications,
                         unread_count=unread_count,
                         reminder_settings=reminder_settings,
                         meal_settings=meal_settings)

@app.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a specific notification as read"""
    user_id = session['user_id']
    notification_service.mark_as_read(notification_id, user_id)
    flash('Notification marked as read', 'success')
    return redirect(url_for('notifications'))

@app.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    user_id = session['user_id']
    notification_service.mark_all_as_read(user_id)
    flash('All notifications marked as read', 'success')
    return redirect(url_for('notifications'))

@app.route('/notifications/delete/<int:notification_id>', methods=['POST'])
@login_required
def delete_notification(notification_id):
    """Delete a notification"""
    user_id = session['user_id']
    notification_service.delete_notification(notification_id, user_id)
    flash('Notification deleted', 'success')
    return redirect(url_for('notifications'))

@app.route('/notifications/update-reminders', methods=['POST'])
@login_required
def update_reminder_settings():
    """Update reminder settings (water and workout reminders)"""
    user_id = session['user_id']
    
    water_reminder = request.form.get('water_reminder') == 'on'
    workout_reminder = request.form.get('workout_reminder') == 'on'
    
    # Update reminder settings
    scheduler.enable_user_reminders(user_id, water=water_reminder, workout=workout_reminder)
    
    # Update meal notification settings
    meal_notifications = request.form.get('meal_notifications') == 'on'
    breakfast_time = request.form.get('breakfast_time', '07:00')
    lunch_time = request.form.get('lunch_time', '13:00')
    snack_time = request.form.get('snack_time', '16:00')
    dinner_time = request.form.get('dinner_time', '19:00')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if settings exist
    cursor.execute('SELECT id FROM notification_settings WHERE user_id = ?', (user_id,))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute('''
            UPDATE notification_settings 
            SET enabled=?, breakfast_time=?, lunch_time=?, snack_time=?, dinner_time=?
            WHERE user_id=?
        ''', (meal_notifications, breakfast_time, lunch_time, snack_time, dinner_time, user_id))
    else:
        cursor.execute('''
            INSERT INTO notification_settings 
            (user_id, enabled, breakfast_time, lunch_time, snack_time, dinner_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, meal_notifications, breakfast_time, lunch_time, snack_time, dinner_time))
    
    conn.commit()
    conn.close()
    
    flash('Reminder settings updated successfully!', 'success')
    return redirect(url_for('notifications'))

@app.route('/api/log-activity', methods=['POST'])
@login_required
def log_activity():
    """
    API endpoint to log daily activity (water intake and workout)
    Used by dashboard for quick logging
    """
    user_id = session['user_id']
    data = request.get_json()
    
    water_intake = data.get('water_intake', 0)
    workout_done = data.get('workout_done', False)
    
    success = analytics_service.log_daily_activity(user_id, water_intake, workout_done)
    
    if success:
        # Check for achievements and send notifications
        if water_intake >= 8:
            notification_service.create_notification(
                user_id,
                'Hydration Goal!',
                '💧 Great job! You drank 8+ glasses of water today!',
                'success'
            )
        
        if workout_done:
            notification_service.create_notification(
                user_id,
                'Workout Complete!',
                '💪 You completed your workout today. Keep it up!',
                'success'
            )
        
        return jsonify({'success': True, 'message': 'Activity logged successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to log activity'}), 500

@app.route('/api/notifications/unread-count', methods=['GET'])
@login_required
def get_unread_count():
    """API endpoint to get unread notification count"""
    user_id = session['user_id']
    count = notification_service.get_unread_count(user_id)
    return jsonify({'count': count})

@app.route('/seed-data', methods=['GET', 'POST'])
@login_required
def seed_sample_data():
    """
    Seed sample fitness data for the current user
    Creates 30 days of realistic data for testing
    """
    user_id = session['user_id']
    
    if request.method == 'POST':
        from seed_data import seed_user_data
        
        try:
            seed_user_data(app.config['DATABASE'], user_id)
            flash('✅ Sample data created! Check your analytics now.', 'success')
        except Exception as e:
            flash(f'❌ Error seeding data: {str(e)}', 'error')
        
        return redirect(url_for('analytics'))
    
    # GET request - show confirmation page
    return render_template('seed_data.html')

# ===== MAIN =====

if __name__ == '__main__':
    init_db()
    
    # Start the scheduler for reminders
    scheduler.start()
    
    # Register cleanup on app shutdown
    atexit.register(lambda: scheduler.shutdown())
    
    print("🚀 HealthCompanion is starting...")
    print("📊 Analytics service initialized")
    print("🔔 Notification service initialized")
    print("⏰ Reminder scheduler started")
    
    app.run(debug=True, port=5000)
