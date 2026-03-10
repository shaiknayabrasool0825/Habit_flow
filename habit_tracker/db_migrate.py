import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'habits.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN theme VARCHAR(20) DEFAULT 'system'")
    except:
        pass
    
    try:
        cursor.execute("""
        CREATE TABLE friendships (
            id INTEGER NOT NULL, 
            user_id INTEGER NOT NULL, 
            friend_id INTEGER NOT NULL, 
            status VARCHAR(20), 
            created_at DATETIME, 
            PRIMARY KEY (id), 
            FOREIGN KEY(user_id) REFERENCES users (id), 
            FOREIGN KEY(friend_id) REFERENCES users (id)
        )
        """)
    except Exception as e:
        print("friendships error:", e)

    conn.commit()
    conn.close()
    print("Database updated!")
