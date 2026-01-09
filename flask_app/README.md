# HealthCompanion - High-Tech Gym Flask Application

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python app.py
```

3. **Access the application:**
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Features

- **High-Tech Gym Theme**: Dark mode with neon accents (cyan, magenta, green)
- **User Authentication**: Registration and login system
- **Health Profile**: Complete biometric data management
- **BMI Calculation**: Real-time BMI analysis with color-coded categories
- **Health Score**: 0-100 score based on multiple health factors
- **Smart Diet Plans**: Personalized nutrition based on goals and activity
- **Progress Analytics**: BMI and health score tracking over time
- **Notifications**: Meal reminder system

## Project Structure

```
flask_app/
├── app.py                  # Main Flask application
├── diet_recommender.py     # Diet recommendation engine
├── requirements.txt        # Python dependencies
├── health_companion.db     # SQLite database (auto-created)
├── static/
│   └── css/
│       └── style.css       # High-tech gym theme styling
└── templates/
    ├── base.html          # Base template
    ├── index.html         # Landing page
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── dashboard.html     # Main dashboard
    ├── profile.html       # Profile management
    ├── diet.html          # Diet recommendations
    ├── analytics.html     # Progress tracking
    └── notifications.html # Notification settings
```

## Database Schema

- **users**: User accounts (email, password, fullname)
- **health_profiles**: User health data (age, gender, height, weight, etc.)
- **bmi_history**: Historical BMI records
- **health_score_history**: Historical health score records
- **notification_settings**: Meal reminder preferences

## Technologies

- **Backend**: Python Flask 3.0
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: High-tech gym theme with neon effects
- **Fonts**: Orbitron (headings), Rajdhani (body)

## Usage

1. **Register** a new account
2. **Login** with your credentials
3. **Set up your health profile** with:
   - Age, Gender, Height, Weight
   - Activity Level, Sleep Hours, Water Intake
   - Medical Conditions, Diet Preference, Fitness Goal
4. **View your dashboard** with BMI, Health Score, and recommendations
5. **Access your personalized diet plan**
6. **Track progress** with analytics charts
7. **Configure meal notifications**

## Color Scheme (High-Tech Gym)

- **Primary Background**: Dark blue/black (`#0a0e1a`)
- **Neon Cyan**: `#00f0ff` (primary accent)
- **Neon Magenta**: `#ff00ff` (secondary accent)
- **Neon Green**: `#00ff88` (success/health)
- **Neon Orange**: `#ffaa00` (warning)
- **Neon Red**: `#ff0055` (danger)

## Security Note

⚠️ This application uses basic password hashing for demonstration. For production use:
- Use stronger secret keys
- Implement HTTPS
- Add CSRF protection
- Use environment variables for sensitive data
- Implement rate limiting

## MCA Project Notes

This project demonstrates:
- Full-stack development with Flask
- Database design and management
- Complex business logic (health calculations)
- Personalized recommendation system
- Data visualization and analytics
- Modern UI/UX design principles
- Responsive web design
