from dotenv import load_dotenv
import os
from app import create_app

# Load .env only in local development
if os.getenv("ENV") != "production":
    load_dotenv()

# Create Flask app (used by Gunicorn)
app = create_app()

# Run locally only
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)