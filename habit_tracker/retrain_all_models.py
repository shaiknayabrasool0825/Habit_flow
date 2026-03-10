from app import app
from ml_logic import train_model
from models import User

def retrain_all_models():
    with app.app_context():
        users = User.query.all()
        for user in users:
            print(f"Retraining model for user: {user.username}")
            try:
                success = train_model(user.id)
                if success:
                    print("  Success!")
                else:
                    print("  Failed (not enough data?)")
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    retrain_all_models()
