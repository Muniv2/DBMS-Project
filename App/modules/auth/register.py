# modules/auth/register.py
from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6 import uic
import os
import sys  # Add this import

class RegisterWindow(QMainWindow):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Load the UI design from file"""
        try:
            # Load the UI file from the ui folder
            ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'register.ui')
            uic.loadUi(ui_path, self)
            print("✅ Register UI loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to load register UI: {e}")
            # Create a basic UI as fallback
            self.create_fallback_ui()
    
    def create_fallback_ui(self):
        """Create a basic UI if the .ui file fails to load"""
        self.setWindowTitle("Create Account - Spotify")
        self.setFixedSize(385, 277)
        print("⚠️  Using fallback UI - some features may not work")
    
    def connect_signals(self):
        """Connect buttons to their functions"""
        try:
            # Find UI elements by their object names from your .ui file
            self.nameBox = self.findChild(QLineEdit, "nameBox")
            self.huIDBox = self.findChild(QLineEdit, "huIDBox")
            self.passwordBox = self.findChild(QLineEdit, "passwordBox")
            self.accountTypeDropDown = self.findChild(QComboBox, "accountTypeDropDown")
            self.createButton = self.findChild(QPushButton, "createButton")
            self.cancelButton = self.findChild(QPushButton, "cancelButton")
            self.loginButton = self.findChild(QPushButton, "createButton_2")  # Note: this is the Login button
            
            # Add items to account type combo box
            self.accountTypeDropDown.clear()
            self.accountTypeDropDown.addItems(["Listener", "Uploader"])
            
            # Connect buttons
            self.createButton.clicked.connect(self.handle_register)
            self.cancelButton.clicked.connect(self.handle_cancel)  # Now exits program
            self.loginButton.clicked.connect(self.handle_login)    # Still goes to login
            
            print("✅ Register UI signals connected successfully!")
            
        except Exception as e:
            print(f"❌ Error connecting UI signals: {e}")
    
    def handle_register(self):
        """Handle user registration"""
        # Get input values
        name = self.nameBox.text().strip()
        huid = self.huIDBox.text().strip()
        password = self.passwordBox.text()
        account_type = self.accountTypeDropDown.currentText()
        
        # Validate inputs
        if not name or not huid or not password:
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields!")
            return
        
        if not huid.isdigit():
            QMessageBox.warning(self, "Invalid HU ID", "HU ID must be a number!")
            return
        
        # Convert to integer for database
        huid_int = int(huid)
        
        # Check database connection
        if not self.main_app.db.connection:
            QMessageBox.critical(self, "Database Error", "Cannot connect to database. Please try again later.")
            return
        
        try:
            # Check if user already exists
            if account_type == "Listener":
                check_query = "SELECT HUID FROM Listener WHERE HUID = ?"
            else:  # Uploader
                check_query = "SELECT HUID FROM Uploader WHERE HUID = ?"
            
            existing_user = self.main_app.db.execute_query(check_query, (huid_int,))
            
            if existing_user and len(existing_user) > 0:
                QMessageBox.warning(self, "User Exists", 
                                  f"HU ID {huid} already exists as a {account_type}. Please use a different HU ID or log in.")
                return
            
            # Insert new user into database
            if account_type == "Listener":
                insert_query = "INSERT INTO Listener (HUID, name, password) VALUES (?, ?, ?)"
                success = self.main_app.db.execute_query(insert_query, (huid_int, name, password))
            else:  # Uploader
                insert_query = "INSERT INTO Uploader (HUID, name, password, totalViewCount, totalLikeCount) VALUES (?, ?, ?, 0, 0)"
                success = self.main_app.db.execute_query(insert_query, (huid_int, name, password))
            
            if success:
                QMessageBox.information(self, "Registration Successful", 
                                      f"Account created successfully!\n\nWelcome {name}!\nAccount Type: {account_type}")
                self.clear_fields()
                self.main_app.switch_to_login()
            else:
                QMessageBox.critical(self, "Registration Failed", 
                                   "Failed to create account. Please try again.")
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred during registration: {str(e)}")
    
    def handle_cancel(self):
        """Handle cancel button - EXIT THE PROGRAM"""
        # Ask for confirmation before exiting
        reply = QMessageBox.question(self, "Exit Program", 
                                   "Are you sure you want to exit?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            print("👋 Exiting Spotify Application...")
            sys.exit(0)  # Exit the program completely
    
    def handle_login(self):
        """Handle login button - go back to login screen"""
        self.main_app.switch_to_login()
    
    def clear_fields(self):
        """Clear all input fields"""
        self.nameBox.clear()
        self.huIDBox.clear()
        self.passwordBox.clear()
        self.accountTypeDropDown.setCurrentIndex(0)
    
    def showEvent(self, event):
        """When the window is shown, clear any previous inputs"""
        super().showEvent(event)
        self.clear_fields()