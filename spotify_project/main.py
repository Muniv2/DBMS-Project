#ALI'S MAIN

# main.py
import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMessageBox

# Import our modules
from database import Database
from modules.auth.login import LoginWindow
from modules.auth.register import RegisterWindow
from modules.uploader.dashboard import UploaderDashboard
from modules.uploader.analytics import AnalyticsWindow

# Simple session management
class SessionManager:
    def __init__(self):
        self.current_user = None
        self.user_name = None
        self.user_role = None
        self.logged_in = False
    
    def login(self, user_id, user_name, role):
        self.current_user = user_id
        self.user_name = user_name
        self.user_role = role
        self.logged_in = True
        print(f"✅ Logged in as {user_name} ({role})")
    
    def logout(self):
        self.current_user = None
        self.user_name = None
        self.user_role = None
        self.logged_in = False
        print("✅ Logged out successfully")

class MainApp:
    def __init__(self):
        print("🎯 Initializing Main Application...")
        
        # Initialize core components
        self.db = Database()
        self.session = SessionManager()
        self.app = QApplication(sys.argv)
        
        # Main widget stack for window management
        self.stacked_widget = QStackedWidget()
        
        # Initialize windows
        self.login_window = LoginWindow(self)
        self.register_window = RegisterWindow(self)
        
        # Will create dashboard when user logs in
        self.uploader_dashboard = None
        self.analytics_window = None
        
        # Add windows to stack
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.register_window)
        
        # Set initial window
        self.stacked_widget.setCurrentWidget(self.login_window)
        self.stacked_widget.setFixedSize(400, 500)
        self.stacked_widget.setWindowTitle("Spotify - Music Streaming")
        self.stacked_widget.show()
    
    def switch_to_register(self):
        """Switch to registration window"""
        self.stacked_widget.setCurrentWidget(self.register_window)
    
    def switch_to_login(self):
        """Switch to login window"""
        # Close the dashboard window if it's open
        if self.uploader_dashboard and self.uploader_dashboard.isVisible():
            self.uploader_dashboard.close()
        
        # Show and switch to the login screen (which is in stacked widget)
        self.stacked_widget.show()
        self.stacked_widget.setCurrentWidget(self.login_window)
        self.stacked_widget.setFixedSize(400, 500)  # Reset to login size
        print("✅ Navigated back to login screen")
    
    def switch_to_uploader_dashboard(self, user_id, user_name):
        """Switch to uploader dashboard"""
         # Create and show the dashboard as a separate window
        self.uploader_dashboard = UploaderDashboard(self, user_id, user_name)
        self.uploader_dashboard.show()
        
        # Hide the main stacked widget (login/register)
        self.stacked_widget.hide()
    
    # ADD THIS NEW METHOD   
    def switch_to_analytics(self, user_id, user_name):
        """Switch to analytics window as separate window"""
        print(f"🎯 Opening analytics for user {user_id}")
        
        # Create and show analytics as separate window (like upload)
        self.analytics_window = AnalyticsWindow(self, user_id, user_name)
        self.analytics_window.show()
        
        # Hide the dashboard (optional)
        if self.uploader_dashboard and self.uploader_dashboard.isVisible():
            self.uploader_dashboard.hide()
        
        print("✅ Analytics window opened as separate window")

    def handle_successful_login(self, user_id, user_name, role):
        """Handle successful login - redirect to appropriate dashboard"""
        print(f"🎉 Login successful! Welcome {user_name} ({role})")
        
        # Store user session
        self.session.login(user_id, user_name, role)
        
        # Redirect based on role
        if role == "Uploader":
            self.switch_to_uploader_dashboard(user_id, user_name)
            QMessageBox.information(self.stacked_widget, "Welcome Uploader!", 
                                  f"Welcome {user_name}!\n\nYou can now upload and monetize your music!")
        else:  # Listener
            QMessageBox.information(self.stacked_widget, "Welcome Listener!", 
                                  f"Welcome {user_name}!\n\nListener features coming soon!")
            # TODO: Add listener dashboard here

# Application entry point
if __name__ == "__main__":
    print("🚀 Starting Spotify Application...")
    print("📝 Testing Complete Upload Flow:")
    print("   1. Login as uploader (ID: 09666)")
    print("   2. Uploader dashboard opens")
    print("   3. Click 'Upload Music'")
    print("   4. Fill upload form")
    print("   5. Upload song with monetization")
    print("   6. Check database for results")
    print("=" * 50)
    
    main_app = MainApp()
    sys.exit(main_app.app.exec())