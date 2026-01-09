import sys
from pathlib import Path

# Add flask_app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'flask_app'))

# Import the Flask app
from app import app

if __name__ == "__main__":
    app.run()
