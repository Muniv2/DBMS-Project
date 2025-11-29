# utils/session_manager.py
print("📦 Session Manager loaded")

class SessionManager:
    def __init__(self):
        self.current_user = None
        self.user_role = None
        print("✅ Session Manager ready")
    
    def login(self, user_id, role):
        self.current_user = user_id
        self.user_role = role
        print(f"✅ User {user_id} logged in as {role}")