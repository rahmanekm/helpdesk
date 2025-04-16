from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig
from sqlalchemy import text

# Initialize SQLAlchemy
db = SQLAlchemy()

# Test database connection
def test_connection():
    try:
        # Use the database URL from your config
        db_url = DevelopmentConfig.SQLALCHEMY_DATABASE_URI
        print(f"Attempting to connect to: {db_url}")
        
        # Create engine
        engine = db.create_engine(db_url)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Successfully connected to MySQL!")
            print("Test query result:", result.scalar())
            
    except Exception as e:
        print("Error connecting to MySQL:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

if __name__ == "__main__":
    test_connection() 