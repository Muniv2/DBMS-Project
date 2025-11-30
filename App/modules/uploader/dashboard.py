# modules/uploader/dashboard.py
from PyQt6.QtWidgets import QMainWindow, QPushButton, QMessageBox , QFileDialog
from PyQt6 import uic
import os

class UploaderDashboard(QMainWindow):
    def __init__(self, main_app, uploader_id, uploader_name):
        super().__init__()
        self.main_app = main_app
        self.uploader_id = uploader_id
        self.uploader_name = uploader_name
        
        # Load the UI file
        ui_path = os.path.join('ui', 'uploader_dashboard(final).ui')
        uic.loadUi(ui_path, self)  # Load into self (QMainWindow)
        
        self.connect_signals()
        print(f"🎯 Uploader Dashboard initialized for {uploader_name} (ID: {uploader_id})")
    
    def connect_signals(self):
        """Connect buttons to functions"""
        try:
            # Connect buttons directly (they're already loaded from UI file)
            self.uploadButton.clicked.connect(self.open_upload)
            self.analyticsButton.clicked.connect(self.open_analytics)
            self.pushButton.clicked.connect(self.logout)  # Logout button
            self.pushButton_3.clicked.connect(self.go_back)  # Back button
            self.uploadPFP.clicked.connect(self.upload_profile_picture)  # Profile picture button
            
            print("✅ Dashboard signals connected!")
        except Exception as e:
            print(f"❌ Error connecting signals: {e}")
    
    def open_upload(self):
        """Open upload window"""
        print(f"🎵 Opening Song Upload for {self.uploader_name}...")
        # QMessageBox.information(self, "Coming Soon", "Upload feature coming soon!")
        # We'll implement the actual upload window after we fix this error

        print(f"🎵 Opening Song Upload for {self.uploader_name}...")
        try:
            from modules.uploader.upload import UploadWindow
            self.upload_window = UploadWindow(self.main_app, self.uploader_id, self.uploader_name)
            self.upload_window.show()
            self.hide()  # Hide dashboard while upload window is open
            print("✅ Upload window opened successfully!")

        except Exception as e:
            print(f"❌ Error opening upload window: {e}")
            QMessageBox.critical(self, "Error", f"Could not open upload window: {str(e)}")
    
    def open_analytics(self):
        """Open analytics"""
        print("🎯 Analytics button clicked!") 
        self.main_app.switch_to_analytics(self.uploader_id, self.uploader_name)

    def upload_profile_picture(self):
        """Upload profile picture"""
        try:
            # Open file dialog to select image
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Select Profile Picture", 
                "", 
                "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
            )
            
            if file_path:
                print(f"📸 Selected profile picture: {file_path}")
                
                # Read the image file as binary
                with open(file_path, 'rb') as file:
                    image_data = file.read()
                
                # Update profile picture in database
                success = self.update_profile_picture(image_data)
                
                if success:
                    QMessageBox.information(self, "Success", "Profile picture updated successfully!")
                    print("✅ Profile picture updated in database")
                else:
                    QMessageBox.warning(self, "Error", "Failed to update profile picture")
                    
        except Exception as e:
            print(f"❌ Error uploading profile picture: {e}")
            QMessageBox.critical(self, "Error", f"Could not upload profile picture: {str(e)}")
    
    def update_profile_picture(self, image_data):
        """Update profile picture in database"""
        try:
            cursor = self.main_app.db.connection.cursor()
            
            # Update the profilePic column for the current uploader
            cursor.execute("""
                UPDATE Uploader 
                SET profilePic = ? 
                WHERE HUID = ?
            """, (image_data, self.uploader_id))
            
            self.main_app.db.connection.commit()
            return True
            
        except Exception as e:
            print(f"❌ Database error updating profile picture: {e}")
            return False

    
    def go_back(self):
        """Go back to login - close dashboard and show login"""
        print("🔙 Back button clicked - returning to login")
        self.close()  # Close dashboard window
        self.main_app.switch_to_login()  # Show login screen

    def logout(self):
        """Logout user - close dashboard and show login"""
        print("🚪 Logging out...")
        
        # Confirm logout
        reply = QMessageBox.question(
            self, 
            "Confirm Logout", 
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.main_app.session.logout()  # Clear session
            self.close()  # Close dashboard window
            self.main_app.switch_to_login()  # Show login screen
            print("✅ Logged out successfully")
        else:
            print("❌ Logout cancelled")
    
    def showEvent(self, event):
        """Show welcome message"""
        super().showEvent(event)
        self.setWindowTitle(f"Welcome {self.uploader_name}!")
        print(f"👋 Welcome, {self.uploader_name}!")