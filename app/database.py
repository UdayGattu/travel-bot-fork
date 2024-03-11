from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Construct the database URL from environment variables
# DATABASE_URL = (
#     f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
#     f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
# )
# DATABASE_URL = 'mysql+pymysql://root:Uday123@@127.0.0.1:3306/mydatabase'
DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# If you're using the declarative base model pattern
from models import Base  # Import the Base from models.py
Base.metadata.create_all(bind=engine)



