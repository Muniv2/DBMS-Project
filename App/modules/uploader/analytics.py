# modules/uploader/analytics.py
print("● Analytics module loaded")

import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt

class AnalyticsWindow(QtWidgets.QMainWindow):
    def __init__(self, main_app, huid, user_name=None):
        super().__init__()
        self.main_app = main_app
        self.huid = huid
        self.user_name = user_name
        
        uic.loadUi('ui/analytics(final).ui', self)
        
        # Debug first to see what's in database
        self.debug_database()
        
        # Initialize UI
        self.setup_ui()
        self.load_analytics_data()
        
        # Connect signals
        self.backButton.clicked.connect(self.go_back)
        self.comboBox.currentIndexChanged.connect(self.update_song_stats)
    
    def setup_ui(self):
        """Initialize UI elements"""
        if self.user_name:
            self.musicCreatorBox.setText(self.user_name)
        
        # Make all boxes read-only
        self.musicCreatorBox.setReadOnly(True)
        self.totalViewCountBox.setReadOnly(True)
        self.totalLikeCountBox.setReadOnly(True)
        self.totalViewCountBox_2.setReadOnly(True)
        self.totalLikeCountBox_2.setReadOnly(True)
    
    def debug_database(self):
        """Check what tables and data actually exist"""
        try:
            cursor = self.main_app.db.connection.cursor()  # ✅ SQL Server connection
            
            # SQL Server syntax to get table names
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            tables = cursor.fetchall()
            print("=== DATABASE DEBUG ===")
            print("Existing tables:", [table[0] for table in tables])
            
            # Check if Song table has data
            if any('Song' in table[0] for table in tables):
                cursor.execute("SELECT TOP 5 * FROM Song")
                songs = cursor.fetchall()
                print("Sample songs:", songs)
            else:
                print("❌ Song table does not exist!")
                
            print("=====================")
            
        except Exception as e:
            print(f"Debug error: {e}")
    
    def get_total_stats(self):
        """Get total views and likes for all songs by this user"""
        try:
            cursor = self.main_app.db.connection.cursor()  # ✅ SQL Server
            
            cursor.execute("""
                SELECT 
                    SUM(s.songViewCount) as totalViews,
                    SUM(s.songLikeCount) as totalLikes  
                FROM Song s
                JOIN Upload u ON s.songID = u.songID
                WHERE u.HUID = ?
            """, (self.huid,))
            
            result = cursor.fetchone()
            total_views = result[0] if result[0] else 0
            total_likes = result[1] if result[1] else 0
            
            return total_views, total_likes
            
        except Exception as e:
            print(f"Error fetching total stats: {e}")
            return 0, 0
    
    def get_user_songs(self):
        """Get all songs uploaded by this user"""
        try:
            cursor = self.main_app.db.connection.cursor()  # ✅ SQL Server
            
            cursor.execute("""
                SELECT 
                    s.songID, s.songName, s.songViewCount, s.songLikeCount
                FROM Song s 
                JOIN Upload u ON s.songID = u.songID
                WHERE u.HUID = ?
                ORDER BY s.songName
            """, (self.huid,))
            
            songs = []
            for row in cursor.fetchall():
                songs.append({
                    'id': row[0],
                    'name': row[1],
                    'views': row[2],
                    'likes': row[3]
                })
            
            return songs
            
        except Exception as e:
            print(f"Error fetching user songs: {e}")
            return []
    
    def get_song_stats(self, song_id):
        """Get views and likes for a specific song"""
        try:
            cursor = self.main_app.db.connection.cursor()  # ✅ SQL Server
            
            cursor.execute("""
                SELECT songViewCount, songLikeCount 
                FROM Song 
                WHERE songID = ?
            """, (song_id,))
            
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
            return 0, 0
            
        except Exception as e:
            print(f"Error fetching song stats: {e}")
            return 0, 0
    
    def load_analytics_data(self):
        """Load all analytics data into the UI"""
        # Temporarily block signals to prevent trigger during population
        self.comboBox.blockSignals(True)
        
        # Load total stats
        total_views, total_likes = self.get_total_stats()
        self.totalViewCountBox.setText(str(total_views))
        self.totalLikeCountBox.setText(str(total_likes))
        
        # Load songs for dropdown
        songs = self.get_user_songs()
        self.comboBox.clear()
        
        if songs:
            for song in songs:
                self.comboBox.addItem(song['name'], song['id'])
            
            # Unblock signals before manually updating
            self.comboBox.blockSignals(False)
            
            # Manually update for first item
            self.update_song_stats()
        else:
            self.totalViewCountBox_2.setText("0")
            self.totalLikeCountBox_2.setText("0")
            self.comboBox.addItem("No songs uploaded")
            self.comboBox.blockSignals(False)
        
    def update_song_stats(self):
        """Update song-specific stats when dropdown selection changes"""
        if self.comboBox.currentData():
            song_id = self.comboBox.currentData()
            views, likes = self.get_song_stats(song_id)
            self.totalViewCountBox_2.setText(str(views))
            self.totalLikeCountBox_2.setText(str(likes))
    
    def go_back(self):
        """Return to uploader dashboard"""
        print("🔙 Analytics back button clicked")
        
        # Show dashboard
        if self.main_app.uploader_dashboard:
            self.main_app.uploader_dashboard.show()
            print("✅ Dashboard shown")
        
        # Close analytics
        self.close()
        print("✅ Analytics window closed")
            