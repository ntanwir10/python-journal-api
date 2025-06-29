import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

print(f"Connection string: {settings.SQLALCHEMY_DATABASE_URI}")
