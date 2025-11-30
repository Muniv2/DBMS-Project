# # modules/uploader/upload.py
# import os
# from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
# from PyQt6 import uic
# from database import Database

# print("@ upload module loaded")

# class UploadWindow(QMainWindow):
#     def __init__(self, main_app, uploader_id, uploader_name):
#         super().__init__()
#         self.main_app = main_app
#         self.uploader_id = uploader_id
#         self.uploader_name = uploader_name
#         self.db = Database()
#         self.selected_file_path = None
        
#         # Load the UI file
#         ui_path = os.path.join('ui', 'upload_music(final).ui')
#         uic.loadUi(ui_path, self)
#         self.setup_connections()
#         print(f"@ upload window ready for {uploader_name} (ID: {uploader_id})")
    
#     def setup_connections(self):
#         """Connect UI signals to methods"""
#         # File selection
#         self.pushButton.clicked.connect(self.select_file)
        
#         # Paid music checkbox
#         self.paidMusicBox.toggled.connect(self.toggle_price_field)
        
#         # Collaborate checkbox
#         self.paidMusicBox_2.toggled.connect(self.toggle_collaborator_field)
        
#         # Upload button
#         self.uploadBox.clicked.connect(self.upload_song)
        
#         # Back button
#         self.backBox.clicked.connect(self.go_back)
    
#     def select_file(self):
#         """Open file dialog to select audio file"""
#         file_path, _ = QFileDialog.getOpenFileName(
#             self, 
#             "Select Audio File", 
#             "", 
#             "Audio Files (*.mp3 *.wav *.ogg *.flac);;All Files (*)"
#         )
        
#         if file_path:
#             self.selected_file_path = file_path
#             filename = os.path.basename(file_path)
#             self.pushButton.setText(f"Selected: {filename[:20]}...")
#             print(f"Selected file: {filename}")
    
#     def toggle_price_field(self, checked):
#         """Enable/disable price field based on paid checkbox"""
#         self.priceBox.setEnabled(checked)
#         if not checked:
#             self.priceBox.clear()
    
#     def toggle_collaborator_field(self, checked):
#         """Enable/disable collaborator field"""
#         self.priceBox_2.setEnabled(checked)
#         if not checked:
#             self.priceBox_2.clear()
    
#     def upload_song(self):
#         """Handle song upload to database"""
#         try:
#             # Get form data
#             track_name = self.trackNameBox.text().strip()
#             genre = self.GenreComboBox.currentText()  # NEW: Get selected genre
#             is_paid = self.paidMusicBox.isChecked()
#             price = self.priceBox.text().strip() if is_paid else "0.00"
#             collaborator_id = self.priceBox_2.text().strip() if self.paidMusicBox_2.isChecked() else None
            
#             # Validation
#             if not track_name:
#                 QMessageBox.warning(self, "Validation Error", "Please enter a track name!")
#                 return
            
#             if not genre:  # NEW: Validate genre
#                 QMessageBox.warning(self, "Validation Error", "Please select a genre!")
#                 return
            
#             if not self.selected_file_path:
#                 QMessageBox.warning(self, "Validation Error", "Please select an audio file!")
#                 return
            
#             if is_paid and not price:
#                 QMessageBox.warning(self, "Validation Error", "Please enter a price for paid music!")
#                 return
            
#             # Convert price to decimal
#             try:
#                 price_value = float(price) if is_paid else 0.0
#                 if is_paid and price_value <= 0:
#                     QMessageBox.warning(self, "Validation Error", "Price must be greater than 0 for paid music!")
#                     return
#             except ValueError:
#                 QMessageBox.warning(self, "Validation Error", "Please enter a valid price!")
#                 return
            
#             # Insert into Song table - UPDATED: Use selected genre
#             song_query = """
#             INSERT INTO Song (songName, genre, paid, price, songFile, songViewCount, songLikeCount)
#             VALUES (?, ?, ?, ?, ?, 0, 0)
#             """
            
#             song_params = (track_name, genre, 1 if is_paid else 0, price_value, os.path.basename(self.selected_file_path))
            
#             if self.db.execute_query(song_query, song_params):
#                 # Get auto-generated song ID
#                 song_id_result = self.db.execute_query("SELECT @@IDENTITY")
#                 if not song_id_result or not song_id_result[0][0]:
#                     song_id_result = self.db.execute_query("SELECT SCOPE_IDENTITY()")
#                 if not song_id_result or not song_id_result[0][0]:
#                     song_id_result = self.db.execute_query("SELECT MAX(songID) FROM Song")

#                 song_id = song_id_result[0][0] if song_id_result and song_id_result[0][0] else None
                
#                 if song_id:
#                     # Create upload relationship
#                     upload_query = "INSERT INTO Upload (HUID, songID) VALUES (?, ?)"
#                     self.db.execute_query(upload_query, (self.uploader_id, song_id))
                    
#                     # Add collaborator if specified
#                     if collaborator_id:
#                         try:
#                             collaborator_id_int = int(collaborator_id)
#                             verify_uploader = self.db.execute_query("SELECT HUID FROM Uploader WHERE HUID = ?", (collaborator_id_int,))
#                             if verify_uploader:
#                                 self.db.execute_query(upload_query, (collaborator_id_int, song_id))
#                                 print(f"Added collaborator: {collaborator_id}")
#                             else:
#                                 QMessageBox.warning(self, "Error", "Collaborator HUID not found!")
#                         except ValueError:
#                             QMessageBox.warning(self, "Error", "Invalid collaborator HUID!")
                    
#                     # Success message
#                     QMessageBox.information(self, "Success", 
#                                           f"Song '{track_name}' uploaded successfully!\nSong ID: {song_id}\nGenre: {genre}")
                    
#                     # Reset form
#                     self.reset_form()
                    
#                     print(f"✅ Song uploaded: {track_name} (ID: {song_id}) by uploader {self.uploader_id}")
#                     print(f"🎵 Genre: {genre}")
                    
#                     # Verify in database
#                     self.verify_upload(song_id, track_name, genre)
                    
#                 else:
#                     QMessageBox.critical(self, "Error", "Failed to get song ID!")
#             else:
#                 QMessageBox.critical(self, "Error", "Failed to upload song to database!")
                
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")
#             print(f"❌ Upload error: {e}")
    
#     def verify_upload(self, song_id, track_name, genre):
#         """Verify the upload was successful"""
#         try:
#             verify_query = """
#             SELECT s.songID, s.songName, s.genre, s.paid, s.price, u.HUID, up.name 
#             FROM Song s
#             JOIN Upload u ON s.songID = u.songID
#             JOIN Uploader up ON u.HUID = up.HUID
#             WHERE s.songID = ?
#             """
#             result = self.db.execute_query(verify_query, (song_id,))
            
#             if result:
#                 print(f"🎉 DATABASE VERIFICATION:")
#                 print(f"   Song: {result[0][1]}")
#                 print(f"   Genre: {result[0][2]}")  # NEW: Show genre
#                 print(f"   Paid: {'Yes' if result[0][3] else 'No'}")
#                 print(f"   Price: ${result[0][4]}")
#                 print(f"   Uploader: {result[0][6]} (ID: {result[0][5]})")
#         except Exception as e:
#             print(f"⚠️ Verification error: {e}")
    
#     def reset_form(self):
#         """Reset the upload form to initial state"""
#         self.trackNameBox.clear()
#         self.GenreComboBox.setCurrentIndex(0)  # NEW: Reset genre to first item
#         self.paidMusicBox.setChecked(False)
#         self.priceBox.clear()
#         self.priceBox.setEnabled(False)
#         self.paidMusicBox_2.setChecked(False)
#         self.priceBox_2.clear()
#         self.priceBox_2.setEnabled(False)
#         self.pushButton.setText("Select File")
#         self.selected_file_path = None
    
#     def go_back(self):
#         """Return to dashboard"""
#         self.close()  # Close upload window
#         if hasattr(self.main_app, 'uploader_dashboard'):
#             self.main_app.uploader_dashboard.show()  # Show dashboard again



# modules/uploader/upload.py
import os
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt6 import uic
from database import Database

print("@ upload module loaded")

class UploadWindow(QMainWindow):
    def __init__(self, main_app, uploader_id, uploader_name):
        super().__init__()
        self.main_app = main_app
        self.uploader_id = uploader_id
        self.uploader_name = uploader_name
        self.db = Database()
        self.selected_file_path = None
        
        # Load the UI file
        ui_path = os.path.join('ui', 'upload_music(final).ui')
        uic.loadUi(ui_path, self)
        self.setup_connections()
        print(f"@ upload window ready for {uploader_name} (ID: {uploader_id})")
    
    def setup_connections(self):
        """Connect UI signals to methods"""
        self.pushButton.clicked.connect(self.select_file)       # Select File
        self.paidMusicBox.toggled.connect(self.toggle_price_field)
        self.paidMusicBox_2.toggled.connect(self.toggle_collaborator_field)
        self.uploadBox.clicked.connect(self.upload_song)        # Upload Song
        self.backBox.clicked.connect(self.go_back)
    
    def select_file(self):
        """Open file dialog to select audio file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Audio File", 
            "", 
            "Audio Files (*.mp3 *.wav *.ogg *.flac);;All Files (*)"
        )
        
        if file_path:
            self.selected_file_path = file_path
            filename = os.path.basename(file_path)
            self.pushButton.setText(f"Selected: {filename[:20]}...")
            print(f"Selected file: {filename}")
    
    def toggle_price_field(self, checked):
        """Enable/disable price field based on paid checkbox"""
        self.priceBox.setEnabled(checked)
        if not checked:
            self.priceBox.clear()
    
    def toggle_collaborator_field(self, checked):
        """Enable/disable collaborator field"""
        self.priceBox_2.setEnabled(checked)
        if not checked:
            self.priceBox_2.clear()
    
    def upload_song(self):
        """Handle song upload to database"""
        try:
            # Get form data
            track_name = self.trackNameBox.text().strip()
            genre = self.GenreComboBox.currentText()
            is_paid = self.paidMusicBox.isChecked()
            price = self.priceBox.text().strip() if is_paid else "0.00"
            collaborator_id = self.priceBox_2.text().strip() if self.paidMusicBox_2.isChecked() else None
            
            # Validation
            if not track_name:
                QMessageBox.warning(self, "Validation Error", "Please enter a track name!")
                return
            
            if not genre:
                QMessageBox.warning(self, "Validation Error", "Please select a genre!")
                return
            
            if not self.selected_file_path:
                QMessageBox.warning(self, "Validation Error", "Please select an audio file!")
                return
            
            if is_paid and not price:
                QMessageBox.warning(self, "Validation Error", "Please enter a price for paid music!")
                return
            
            # Convert price to decimal
            try:
                price_value = float(price) if is_paid else 0.0
                if is_paid and price_value <= 0:
                    QMessageBox.warning(self, "Validation Error", "Price must be greater than 0 for paid music!")
                    return
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Please enter a valid price!")
                return
            
            # 🔥 INSERT song with artistName included
            song_query = """
            INSERT INTO Song (songName, genre, paid, price, songFile, artistName, songViewCount, songLikeCount)
            VALUES (?, ?, ?, ?, ?, ?, 0, 0)
            """
            
            song_params = (
                track_name,
                genre,
                1 if is_paid else 0,
                price_value,
                os.path.basename(self.selected_file_path),
                self.uploader_name   # 🔥 ARTIST NAME INSERTED HERE
            )
            
            if self.db.execute_query(song_query, song_params):
                
                # Get auto-generated song ID
                song_id_result = self.db.execute_query("SELECT SCOPE_IDENTITY()")
                if not song_id_result or not song_id_result[0][0]:
                    song_id_result = self.db.execute_query("SELECT MAX(songID) FROM Song")

                song_id = song_id_result[0][0]
                
                if song_id:
                    # Create upload relationship
                    upload_query = "INSERT INTO Upload (HUID, songID) VALUES (?, ?)"
                    self.db.execute_query(upload_query, (self.uploader_id, song_id))
                    
                    # Add collaborator if given
                    if collaborator_id:
                        try:
                            collaborator_id_int = int(collaborator_id)
                            verify = self.db.execute_query("SELECT HUID FROM Uploader WHERE HUID = ?", (collaborator_id_int,))
                            
                            if verify:
                                self.db.execute_query(upload_query, (collaborator_id_int, song_id))
                                print(f"Added collaborator: {collaborator_id}")
                            else:
                                QMessageBox.warning(self, "Error", "Collaborator HUID not found!")
                        except ValueError:
                            QMessageBox.warning(self, "Error", "Invalid collaborator HUID!")
                    
                    # SUCCESS MESSAGE
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Song '{track_name}' uploaded successfully!\n"
                        f"Song ID: {song_id}\nGenre: {genre}\nArtist: {self.uploader_name}"
                    )
                    
                    # Reset form
                    self.reset_form()
                    
                    print(f"✅ Song uploaded: {track_name} (ID: {song_id}) by {self.uploader_name}")
                    print(f"🎵 Genre: {genre}")
                    
                    # Verify in database
                    self.verify_upload(song_id, track_name, genre)
                
                else:
                    QMessageBox.critical(self, "Error", "Failed to get song ID!")
            else:
                QMessageBox.critical(self, "Error", "Failed to upload song to database!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")
            print(f"❌ Upload error: {e}")
    
    def verify_upload(self, song_id, track_name, genre):
        """Verify the upload was successful"""
        try:
            verify_query = """
            SELECT songID, songName, genre, paid, price, artistName
            FROM Song
            WHERE songID = ?
            """
            result = self.db.execute_query(verify_query, (song_id,))
            
            if result:
                print("🎉 DATABASE VERIFICATION:")
                print(f"   Song: {result[0][1]}")
                print(f"   Genre: {result[0][2]}")
                print(f"   Paid: {'Yes' if result[0][3] else 'No'}")
                print(f"   Price: ${result[0][4]}")
                print(f"   Artist: {result[0][5]}")
        except Exception as e:
            print(f"⚠️ Verification error: {e}")
    
    def reset_form(self):
        """Reset the upload form to initial state"""
        self.trackNameBox.clear()
        self.GenreComboBox.setCurrentIndex(0)
        self.paidMusicBox.setChecked(False)
        self.priceBox.clear()
        self.priceBox.setEnabled(False)
        self.paidMusicBox_2.setChecked(False)
        self.priceBox_2.clear()
        self.priceBox_2.setEnabled(False)
        self.pushButton.setText("Select File")
        self.selected_file_path = None
    
    def go_back(self):
        """Return to dashboard"""
        self.close()
        if hasattr(self.main_app, 'uploader_dashboard'):
            self.main_app.uploader_dashboard.show()
