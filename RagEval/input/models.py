from database import Database

class UserModel:
    def __init__(self, db: Database):
        self.db = db

    def create_user(self, username: str, email: str):
        query = f"INSERT INTO users (username, email) VALUES ('{username}', '{email}')"
        return self.db.execute_query(query)

    def find_user(self, user_id: int):
        query = f"SELECT * FROM users WHERE id = {user_id}"
        return self.db.execute_query(query)