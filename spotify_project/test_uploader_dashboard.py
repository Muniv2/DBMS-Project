# test_uploader_dashboard.py - YOUR PERSONAL TEST FILE
import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMessageBox

# Import existing modules
from database import Database
from modules.auth.login import LoginWindow
from modules.auth.register import RegisterWindow

# Import YOUR new uploader dashboard
from modules.uploader.dashboard import UploaderDashboard

class SessionManager:
    def __init__(self):
        self.current_user = None
        self.user_name = None
        self.user_role = None
    
    def login(self, user_id, user_name, role):
        self.current_user = user_id
        self.user_name = user_name
        self.user_role = role
        print(f"✅ Logged in as {user_name} ({role})")
    
    def logout(self):
        self.current_user = None
        self.user_name = None
        self.user_role = None

class TestApp:
    def __init__(self):
        print("🧪 TESTING UPLOADER DASHBOARD...")
        
        # Initialize components
        self.db = Database()
        self.session = SessionManager()
        self.app = QApplication(sys.argv)
        
        # Main widget stack
        self.stacked_widget = QStackedWidget()
        
        # Initialize windows
        self.login_window = LoginWindow(self)
        self.register_window = RegisterWindow(self)
        self.uploader_dashboard = UploaderDashboard(self, uploader_id=1, uploader_name="Test Uploader")  # YOUR NEW DASHBOARD
        
        # Add to stack
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.register_window)
        self.stacked_widget.addWidget(self.uploader_dashboard)
        
        # Start with login
        self.stacked_widget.setCurrentWidget(self.login_window)
        self.stacked_widget.setFixedSize(400, 500)
        self.stacked_widget.setWindowTitle("TEST - Spotify Uploader Dashboard")
        self.stacked_widget.show()
    
    def switch_to_register(self):
        self.stacked_widget.setCurrentWidget(self.register_window)
    
    def switch_to_login(self):
        self.stacked_widget.setCurrentWidget(self.login_window)
    
    def handle_successful_login(self, user_id, user_name, role):
        print(f"🎉 Login successful! Welcome {user_name} ({role})")
        
        # Store session
        self.session.login(user_id, user_name, role)
        
        # Redirect uploaders to YOUR dashboard
        if role == "Uploader":
            self.stacked_widget.setCurrentWidget(self.uploader_dashboard)
            QMessageBox.information(self.stacked_widget, "TEST SUCCESS", 
                                  f"Welcome {user_name}!\nUploader Dashboard WORKING!")
        else:
            QMessageBox.information(self.stacked_widget, "Listener", 
                                  "Listener features not in this test")

if __name__ == "__main__":
    test_app = TestApp()
    sys.exit(test_app.app.exec())
