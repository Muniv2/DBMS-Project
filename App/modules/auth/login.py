# modules/auth/login.py
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6 import uic
import os

class LoginWindow(QDialog):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Load the UI design from file"""
        try:
            # Load the UI file from the ui folder
            ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'login.ui')
            uic.loadUi(ui_path, self)
            print("✅ Login UI loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to load login UI: {e}")
            # Create a basic UI as fallback
            self.create_fallback_ui()
    
    def create_fallback_ui(self):
        """Create a basic UI if the .ui file fails to load"""
        self.setWindowTitle("Login - Spotify")
        self.setFixedSize(327, 408)
        
        # Note: Fallback UI would need to match your exact layout
        # For now, we'll rely on the .ui file working
        print("⚠️  Using fallback UI - some features may not work")
    
    def connect_signals(self):
        """Connect buttons to their functions"""
        try:
            # Find UI elements by their object names from your .ui file
            self.huID_line = self.findChild(QLineEdit, "huID_line")
            self.password_line = self.findChild(QLineEdit, "password_line") 
            self.comboBox = self.findChild(QComboBox, "comboBox")
            self.loginButton = self.findChild(QPushButton, "loginButton")
            self.registerButton = self.findChild(QPushButton, "pushButton")  # New register button
            
            # Add items to combo box (Listener and Uploader)
            self.comboBox.clear()
            self.comboBox.addItems(["Listener", "Uploader"])
            
            # Connect buttons
            self.loginButton.clicked.connect(self.handle_login)
            self.registerButton.clicked.connect(self.handle_register)  # Connect register button
            
            print("✅ Login UI signals connected successfully!")
            
        except Exception as e:
            print(f"❌ Error connecting UI signals: {e}")
    
    def handle_login(self):
        """Validate user credentials and log them in"""
        # Get input values
        huid = self.huID_line.text().strip()
        password = self.password_line.text()
        role = self.comboBox.currentText()
        
        # Validate inputs
        if not huid or not password:
            QMessageBox.warning(self, "Missing Information", "Please enter both HU ID and password!")
            return
        
        if not huid.isdigit():
            QMessageBox.warning(self, "Invalid HU ID", "HU ID must be a number!")
            return
        
        # Convert to integer for database query
        huid_int = int(huid)
        
        # Check database connection
        if not self.main_app.db.connection:
            QMessageBox.critical(self, "Database Error", "Cannot connect to database. Please try again later.")
            return
        
        try:
            # Query database based on role
            if role == "Listener":
                query = "SELECT HUID, name FROM Listener WHERE HUID = ? AND password = ?"
            else:  # Uploader
                query = "SELECT HUID, name FROM Uploader WHERE HUID = ? AND password = ?"
            
            # Execute query
            results = self.main_app.db.execute_query(query, (huid_int, password))
            
            if results and len(results) > 0:
                # Login successful
                user_id = results[0][0]
                user_name = results[0][1]
                
                print(f"✅ Login successful: {user_name} ({role})")
                
                # Call main app to handle successful login
                self.main_app.handle_successful_login(user_id, user_name, role)
                
            else:
                # Login failed
                QMessageBox.warning(self, "Login Failed", 
                                  "Invalid HU ID or password. Please try again.")
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred during login: {str(e)}")
    
    def handle_register(self):
        """Switch to registration window when Register button is clicked"""
        self.main_app.switch_to_register()
    
    def clear_fields(self):
        """Clear all input fields"""
        self.huID_line.clear()
        self.password_line.clear()
        self.comboBox.setCurrentIndex(0)
    
    def showEvent(self, event):
        """When the window is shown, clear any previous inputs"""
        super().showEvent(event)
        self.clear_fields()