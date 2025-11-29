# main.py
import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMessageBox

# Import our modules
from database import Database
from modules.auth.login import LoginWindow
from modules.auth.register import RegisterWindow

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
        
        # Add windows to stack
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.register_window)
        
        # Set initial window
        self.stacked_widget.setCurrentWidget(self.login_window)
        self.stacked_widget.setFixedSize(400, 500)
        self.stacked_widget.setWindowTitle("Spotify - Music Waiting")
        self.stacked_widget.show()
    
    def switch_to_register(self):
        """Switch to registration window"""
        self.stacked_widget.setCurrentWidget(self.register_window)
    
    def switch_to_login(self):
        """Switch to login window"""
        self.stacked_widget.setCurrentWidget(self.login_window)
    
    def handle_successful_login(self, user_id, user_name, role):
        """Handle successful login - redirect to appropriate dashboard"""
        print(f"🎉 Login successful! Welcome {user_name} ({role})")
        
        # Store user session
        self.session.login(user_id, user_name, role)
        
        # Show success message
        QMessageBox.information(self.stacked_widget, "Login Successful", 
                              f"Welcome {user_name}!\n\nRole: {role}\n\n(Redirect to dashboard coming soon)")
        
        # TODO: Redirect based on role (will be implemented by Person B & C)
        # if role == "Uploader":
        #     self.stacked_widget.setCurrentWidget(self.uploader_dashboard)
        # else:  # Listener
        #     self.stacked_widget.setCurrentWidget(self.search_window)

# Application entry point
if __name__ == "__main__":
    print("🚀 Starting Spotify Application...")
    main_app = MainApp()
    sys.exit(main_app.app.exec())