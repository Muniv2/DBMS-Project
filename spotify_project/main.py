# main.py
print("🚀 Starting Spotify Application...")

# Import our modules
from database import Database
from modules.auth.login import LoginWindow
from modules.auth.register import RegisterWindow
from modules.uploader.dashboard import UploaderDashboard
from modules.listener.dashboard import ListenerDashboard

class MainApp:
    def __init__(self):
        print("🎯 Initializing Main Application...")
        
        # Initialize core components
        self.db = Database()
        
        # Initialize all windows
        self.login_window = LoginWindow(self)
        self.register_window = RegisterWindow(self)
        self.uploader_dashboard = UploaderDashboard(self)
        self.listener_dashboard = ListenerDashboard(self)
        
        print("✅ All modules loaded successfully!")
        print("\n📋 Team Assignments:")
        print("   Person A: Login & Register (modules/auth/)")
        print("   Person B: Uploader Features (modules/uploader/)") 
        print("   Person C: Listener Features (modules/listener/)")
        print("\n🎉 Skeleton ready! Everyone can start coding.")

if __name__ == "__main__":
    app = MainApp()
    