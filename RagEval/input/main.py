from database import Database
from models import UserModel

class Application:
    def __init__(self):
        self.db = Database("postgresql://localhost:5432/mydb")
        self.user_model = UserModel(self.db)

    def run(self):
        self.db.connect()
        print("Application started.")

    def register_new_user(self, username: str, email: str):
        print(f"Registering user: {username}")
        return self.user_model.create_user(username, email)

if __name__ == "__main__":
    app = Application()
    app.run()
    app.register_new_user("alice", "alice@example.com")