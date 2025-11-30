from database import Database

def test_connection():
    db = Database()
    try:
        # Test query - get all users
        users = db.execute_query("SELECT * FROM users")
        print("Database connection successful!")
        print("Users in database:")
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[3]}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()