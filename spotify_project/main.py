# # main.py
# import sys
# from PyQt6.QtWidgets import QApplication, QStackedWidget, QMessageBox

# # Import our modules
# from database import Database
# from modules.auth.login import LoginWindow
# from modules.auth.register import RegisterWindow

# # Simple session management
# class SessionManager:
#     def __init__(self):
#         self.current_user = None
#         self.user_name = None
#         self.user_role = None
#         self.logged_in = False
    
#     def login(self, user_id, user_name, role):
#         self.current_user = user_id
#         self.user_name = user_name
#         self.user_role = role
#         self.logged_in = True
#         print(f"✅ Logged in as {user_name} ({role})")
    
#     def logout(self):
#         self.current_user = None
#         self.user_name = None
#         self.user_role = None
#         self.logged_in = False
#         print("✅ Logged out successfully")

# class MainApp:
#     def __init__(self):
#         print("🎯 Initializing Main Application...")
        
#         # Initialize core components
#         self.db = Database()
#         self.session = SessionManager()
#         self.app = QApplication(sys.argv)
        
#         # Main widget stack for window management
#         self.stacked_widget = QStackedWidget()
        
#         # Initialize windows
#         self.login_window = LoginWindow(self)
#         self.register_window = RegisterWindow(self)
        
#         # Add windows to stack
#         self.stacked_widget.addWidget(self.login_window)
#         self.stacked_widget.addWidget(self.register_window)
        
#         # Set initial window
#         self.stacked_widget.setCurrentWidget(self.login_window)
#         self.stacked_widget.setFixedSize(400, 500)
#         self.stacked_widget.setWindowTitle("Spotify - Music Waiting")
#         self.stacked_widget.show()
    
#     def switch_to_register(self):
#         """Switch to registration window"""
#         self.stacked_widget.setCurrentWidget(self.register_window)
    
#     def switch_to_login(self):
#         """Switch to login window"""
#         self.stacked_widget.setCurrentWidget(self.login_window)
    
#     def handle_successful_login(self, user_id, user_name, role):
#         """Handle successful login - redirect to appropriate dashboard"""
#         print(f"🎉 Login successful! Welcome {user_name} ({role})")
        
#         # Store user session
#         self.session.login(user_id, user_name, role)
        
#         # Show success message
#         QMessageBox.information(self.stacked_widget, "Login Successful", 
#                               f"Welcome {user_name}!\n\nRole: {role}\n\n(Redirect to dashboard coming soon)")
        
#         # TODO: Redirect based on role (will be implemented by Person B & C)
#         # if role == "Uploader":
#         #     self.stacked_widget.setCurrentWidget(self.uploader_dashboard)
#         # else:  # Listener
#         #     self.stacked_widget.setCurrentWidget(self.search_window)

# # Application entry point
# if __name__ == "__main__":
#     print("🚀 Starting Spotify Application...")
#     main_app = MainApp()
#     sys.exit(main_app.app.exec())


# main.py
import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMessageBox

# Import our modules
from database import Database
from modules.auth.login import LoginWindow
from modules.auth.register import RegisterWindow
from modules.listener.search import SearchWindow
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
        
        # Main widget stack for window management (for Login, Register, Listener)
        self.stacked_widget = QStackedWidget()
        
        # Initialize windows that use stacked widget
        self.login_window = LoginWindow(self)
        self.register_window = RegisterWindow(self)
        self.search_window = SearchWindow(self)  # Listener dashboard
        
        # Uploader windows (will be created when needed)
        self.uploader_dashboard = None
        self.analytics_window = None
        
        # Add stacked windows to stack
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.register_window)
        self.stacked_widget.addWidget(self.search_window)
        
        # Set initial window
        self.stacked_widget.setCurrentWidget(self.login_window)
        self.stacked_widget.setFixedSize(400, 500)  # Default size for login/register
        self.stacked_widget.setWindowTitle("Spotify - Music Waiting")
        self.stacked_widget.show()
    
    def switch_to_register(self):
        """Switch to registration window"""
        self.stacked_widget.setFixedSize(400, 500)  # Register size
        self.stacked_widget.setCurrentWidget(self.register_window)
    
    def switch_to_login(self):
        """Switch to login window"""
        self.stacked_widget.setFixedSize(400, 500)  # Login size
        self.stacked_widget.setCurrentWidget(self.login_window)
    
    def switch_to_listener_dashboard(self):
        """Switch to listener search/dashboard"""
        self.stacked_widget.setFixedSize(548, 391)  # Search screen size
        self.stacked_widget.setCurrentWidget(self.search_window)
        print("🔄 Switched to Listener Dashboard")
    
    def switch_to_uploader_dashboard(self, user_id, user_name):
        """Switch to uploader dashboard as separate window"""
        # Create uploader dashboard if not exists
        if not self.uploader_dashboard:
            self.uploader_dashboard = UploaderDashboard(self, user_id, user_name)
        
        # Hide the stacked widget (login/register/listener)
        self.stacked_widget.hide()
        
        # Show uploader dashboard
        self.uploader_dashboard.show()
        print("🔄 Switched to Uploader Dashboard")
    
    def switch_to_analytics(self, user_id, user_name):
        """Switch to analytics window as separate window"""
        print(f"🎯 Opening analytics for user {user_id}")
        
        # Create analytics window
        self.analytics_window = AnalyticsWindow(self, user_id, user_name)
        self.analytics_window.show()
        
        # Hide the dashboard (optional)
        if self.uploader_dashboard and self.uploader_dashboard.isVisible():
            self.uploader_dashboard.hide()
        
        print("✅ Analytics window opened")
    
    def handle_successful_login(self, user_id, user_name, role):
        """Handle successful login - redirect to appropriate dashboard"""
        print(f"🎉 Login successful! Welcome {user_name} ({role})")
        
        # Store user session
        self.session.login(user_id, user_name, role)
        
        # Redirect based on role
        if role == "Uploader":
            self.switch_to_uploader_dashboard(user_id, user_name)
            QMessageBox.information(None, "Welcome Uploader!", 
                                  f"Welcome {user_name}!\n\nYou can now upload and monetize your music!")
        else:  # Listener
            self.switch_to_listener_dashboard()
            QMessageBox.information(self.stacked_widget, "Welcome Listener!", 
                                  f"Welcome {user_name}!\n\nYou can now search and play music!")
    
    def logout_user(self):
        """Handle user logout from any screen"""
        # Close all uploader windows
        if self.uploader_dashboard and self.uploader_dashboard.isVisible():
            self.uploader_dashboard.close()
            self.uploader_dashboard = None
        
        if self.analytics_window and self.analytics_window.isVisible():
            self.analytics_window.close()
            self.analytics_window = None
        
        # Show the stacked widget and switch to login
        self.stacked_widget.show()
        self.switch_to_login()
        
        # Clear session
        self.session.logout()
        
        print("✅ User logged out successfully")

# Application entry point
if __name__ == "__main__":
    print("🚀 Starting Spotify Application...")
    print("=" * 50)
    print("📝 Available Test Accounts:")
    print("   Listener: HUID=1001, Password=pass123")
    print("   Uploader: HUID=2001, Password=upload123") 
    print("=" * 50)
    
    main_app = MainApp()
    sys.exit(main_app.app.exec())