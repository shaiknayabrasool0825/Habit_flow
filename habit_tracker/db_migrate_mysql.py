import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("No DATABASE_URL found in .env")
    exit(1)

engine = create_engine(db_url)

with engine.connect() as conn:
    print("Connected to database. Checking columns...")
    
    # Check if timezone column exists
    try:
        conn.execute(text("SELECT timezone FROM users LIMIT 1"))
        print("Column 'timezone' already exists.")
    except Exception:
        print("Adding 'timezone' column...")
        conn.execute(text("ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC'"))

    # Check if theme column exists
    try:
        conn.execute(text("SELECT theme FROM users LIMIT 1"))
        print("Column 'theme' already exists.")
    except Exception:
        print("Adding 'theme' column...")
        conn.execute(text("ALTER TABLE users ADD COLUMN theme VARCHAR(20) DEFAULT 'system'"))
        
    # Check friendships table
    try:
        conn.execute(text("SELECT id FROM friendships LIMIT 1"))
        print("Table 'friendships' already exists.")
    except Exception:
        print("Creating 'friendships' table...")
        conn.execute(text("""
        CREATE TABLE friendships (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            user_id INT NOT NULL, 
            friend_id INT NOT NULL, 
            status VARCHAR(20) DEFAULT 'pending', 
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
            FOREIGN KEY(user_id) REFERENCES users(id), 
            FOREIGN KEY(friend_id) REFERENCES users(id)
        )
        """))
    
    conn.commit()
    print("MySQL Database schema updated successfully!")
