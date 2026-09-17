class Database:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def connect(self):
        print(f"Connecting to database at {self.db_url}")
        return True

    def execute_query(self, query: str):
        print(f"Executing query: {query}")
        return {"status": "success"}