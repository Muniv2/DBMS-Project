from PyQt6.QtWidgets import (
    QDialog, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6 import uic
import os

print("📦 Search module loaded")


class SearchWindow(QDialog):
    def __init__(self, main_app):
        super().__init__()
        self.selected_song = None
        self.main_app = main_app
        self.search_results_list = None
        self.purchased_list = None
        self.setup_ui()
        self.connect_signals()
        # safe: loading purchased songs now — if user not logged in, it will simply do nothing
        self.load_purchased_songs()

    def setup_ui(self):
        """Load UI"""
        try:
            ui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'search_play.ui')
            uic.loadUi(ui_path, self)
            print("✅ Search UI loaded successfully!")
        except Exception as e:
            print(f"❌ Failed to load search UI: {e}")
            self.create_fallback_ui()

    def create_fallback_ui(self):
        self.setWindowTitle("Search Songs - Spotify")
        self.setFixedSize(800, 500)

    def connect_signals(self):
        try:
            # find widgets (these names must match your .ui)
            self.artistName = self.findChild(QLineEdit, "artistName")
            self.genreName = self.findChild(QLineEdit, "genreName")
            self.songName = self.findChild(QLineEdit, "songName")

            self.search_button = self.findChild(QPushButton, "searchButton")
            self.play_button = self.findChild(QPushButton, "PlayButton")
            self.purchase_button = self.findChild(QPushButton, "PurchaseButton")
            self.logout_button = self.findChild(QPushButton, "logOut")
            self.like_button = self.findChild(QPushButton, "LikeButton")

            # Make sure like_button exists before calling methods on it
            if self.like_button is not None:
                self.like_button.setCheckable(True)
                self.like_button.setEnabled(False)

            self.search_results_list = self.findChild(QListWidget, "searchResults")
            self.purchased_list = self.findChild(QListWidget, "purchasedSongs")

            # Connect signals only if widgets were found
            if self.search_button is not None:
                self.search_button.clicked.connect(self.handle_search)
            if self.play_button is not None:
                self.play_button.clicked.connect(self.handle_play)
            if self.purchase_button is not None:
                self.purchase_button.clicked.connect(self.handle_purchase)
            if self.logout_button is not None:
                self.logout_button.clicked.connect(self.handle_logout)
            if self.like_button is not None:
                self.like_button.clicked.connect(self.handle_like)
            if self.search_results_list is not None:
                self.search_results_list.itemSelectionChanged.connect(self.update_selected_song)
            if self.purchased_list is not None:
                self.purchased_list.itemSelectionChanged.connect(self.update_selected_song)

            print("✅ Search UI signals connected!")
        except Exception as e:
            print(f"❌ Error connecting signals: {e}")

    # ===================== HELPER =====================
    def get_listener_id(self):
        """
        Correctly and safely fetch the logged-in listener id from SessionManager.
        Your SessionManager stores the HUID in `current_user`, so use that.
        """
        sess = getattr(self.main_app, "session", None)
        if not sess:
            return None
        return getattr(sess, "current_user", None)

    # ===================== LOAD PURCHASED SONGS =====================
    def load_purchased_songs(self):
        """Populate purchased songs list for current listener."""
        # DB connection required
        if not getattr(self.main_app, "db", None) or not getattr(self.main_app.db, "connection", None):
            return

        listener_id = self.get_listener_id()
        if listener_id is None:
            # not logged in yet — this is normal if called early; bail out gracefully
            print("⚠️ No listener ID found in session (load_purchased_songs). Skipping.")
            return

        # purchased_list must exist in UI
        if self.purchased_list is None:
            print("❌ Purchased list widget not found (load_purchased_songs).")
            return

        try:
            results = self.main_app.db.execute_query(
                """
                SELECT s.songID, s.songName, s.songFile, s.artistName, s.genre
                FROM Song s
                JOIN Purchase p ON s.songID = p.songID
                WHERE p.HUID = ?
                """,
                (listener_id,)
            )

            # clear and populate purchased_list
            self.purchased_list.clear()
            for songID, songName, songFile, artist, genre in results:
                item = QListWidgetItem(f"{songName} - {artist or 'Unknown'} [{genre or 'Unknown'}]")
                item.setData(256, {
                    "songID": songID,
                    "songName": songName,
                    "songFile": songFile,
                    "paid": 1,
                    "purchased": True
                })
                self.purchased_list.addItem(item)

            print(f"💰 Loaded {len(results)} purchased songs for HUID={listener_id}.")

            # Print details to terminal as requested
            print("📄 Purchased songs details for user:", listener_id)
            for songID, songName, songFile, artist, genre in results:
                print(f"ID: {songID}, Name: {songName}, File: {songFile}, Artist: {artist}, Genre: {genre}")

        except Exception as e:
            print("❌ Error loading purchased songs:", e)

    # ===================== SEARCH =====================
    def handle_search(self):
        artist = (self.artistName.text().strip() if self.artistName else "")
        genre = (self.genreName.text().strip() if self.genreName else "")
        song_name = (self.songName.text().strip() if self.songName else "")

        if not getattr(self.main_app, "db", None) or not getattr(self.main_app.db, "connection", None):
            QMessageBox.critical(self, "Database Error", "Cannot connect to database.")
            return

        try:
            query = """
                SELECT songID, songName, genre, artistName, paid, price, songFile
                FROM Song
            """
            conditions = []
            params = []

            if artist:
                conditions.append("LOWER(TRIM(artistName)) LIKE LOWER(TRIM(?))")
                params.append(f"%{artist}%")
            if genre:
                conditions.append("LOWER(TRIM(genre)) LIKE LOWER(TRIM(?))")
                params.append(f"%{genre}%")
            if song_name:
                conditions.append("LOWER(TRIM(songName)) LIKE LOWER(TRIM(?))")
                params.append(f"%{song_name}%")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            results = self.main_app.db.execute_query(query, tuple(params))

            if self.search_results_list is None:
                print("❌ searchResults widget not found (handle_search).")
                return

            self.search_results_list.clear()
            self.selected_song = None
            if self.like_button is not None:
                self.like_button.setEnabled(False)

            if results:
                listener_id = self.get_listener_id()
                for songID, songName, genre, artistName, paid, price, songFile in results:
                    purchased = False
                    if listener_id and paid:
                        check = self.main_app.db.execute_query(
                            "SELECT 1 FROM Purchase WHERE HUID = ? AND songID = ?",
                            (listener_id, songID)
                        )
                        purchased = bool(check)

                    item = QListWidgetItem(f"{songName} - {artistName or 'Unknown'} [{genre or 'Unknown'}]")
                    item.setData(256, {
                        "songID": songID,
                        "songName": songName,
                        "songFile": songFile,
                        "artistName": artistName, 
                        "price": price,
                        "paid": paid,
                        "purchased": purchased
                    })
                    self.search_results_list.addItem(item)
            else:
                QMessageBox.information(self, "No Results", "No songs match your search.")
        except Exception as e:
            print("❌ Search error:", e)

    # ===================== SELECTION =====================
    def update_selected_song(self):
        """Update selected song from either list (works for both lists)."""
        # prefer sender, but fallback to whichever has a selection
        sender = self.sender()
        item = None
        if sender is not None and hasattr(sender, "currentItem"):
            item = sender.currentItem()
        if item is None:
            # fallback: prefer search_results_list selection, else purchased_list
            if self.search_results_list is not None:
                item = self.search_results_list.currentItem()
            if item is None and self.purchased_list is not None:
                item = self.purchased_list.currentItem()

        if item:
            song_data = item.data(256)
            self.selected_song = song_data
            print(f"[Selected] {song_data['songID']} - {song_data['songName']}")

            # Enable like button only if song is free or purchased
            if self.like_button is not None:
                self.like_button.setEnabled(not song_data.get("paid") or song_data.get("purchased"))

            # Set like button based on previous likes (unchanged logic)
            result = self.main_app.db.execute_query(
                "SELECT songLikeCount FROM Song WHERE songID = ?", 
                (song_data["songID"],)
            )
            like_count = result[0][0] if result else 0
            if self.like_button is not None:
                self.like_button.setChecked(like_count > 0)
        else:
            self.selected_song = None
            if self.like_button is not None:
                self.like_button.setEnabled(False)

    # ===================== PLAY =====================
    def handle_play(self):
        if not self.selected_song:
            QMessageBox.warning(self, "Select Song", "Please select a song first!")
            return

        song = self.selected_song

        if song.get("paid") and not song.get("purchased"):
            QMessageBox.information(self, "Purchase Required", "Please purchase this song first!")
            return

        song_id = song["songID"]
        print(f"🎧 Playing: {song['songName']} ({song['songFile']})")

        try:
            self.main_app.db.execute_query(
                "UPDATE Song SET songViewCount = songViewCount + 1 WHERE songID = ?",
                (song_id,)
            )
            QMessageBox.information(self, "Playing", f"Now playing: {song['songName']}")
        except Exception as e:
            print("❌ Error updating view count:", e)

    # ===================== LIKE =====================
    def handle_like(self):
        if not self.selected_song:
            return

        song = self.selected_song
        if song.get("paid") and not song.get("purchased"):
            QMessageBox.information(self, "Purchase Required", "Please purchase this song first!")
            # keep original behavior: undo the check
            if self.like_button is not None:
                self.like_button.setChecked(False)
            return

        song_id = song["songID"]
        liked = self.like_button.isChecked() if self.like_button else False

        try:
            if liked:
                self.main_app.db.execute_query(
                    "UPDATE Song SET songLikeCount = songLikeCount + 1 WHERE songID = ?",
                    (song_id,)
                )
            else:
                self.main_app.db.execute_query(
                    "UPDATE Song SET songLikeCount = songLikeCount - 1 WHERE songID = ? AND songLikeCount > 0",
                    (song_id,)
                )
        except Exception as e:
            print("❌ Error updating like count:", e)

    # ===================== PURCHASE =====================
    def handle_purchase(self):
        if not self.selected_song:
            QMessageBox.warning(self, "Select Song", "Please select a song first!")
            return

        song = self.selected_song

        if not song.get("paid"):
            QMessageBox.information(self, "Song Already Free", "This song is already free!")
            return

        if song.get("purchased"):
            QMessageBox.information(self, "Already Purchased", "You have already purchased this song.")
            return

        # ✅ Ensure purchase_window exists
        if not hasattr(self.main_app, "purchase_window") or not self.main_app.purchase_window:
            from modules.listener.purchase import PurchaseWindow
            self.main_app.purchase_window = PurchaseWindow(self.main_app)

        # ✅ Ensure it's in the stacked widget
        if self.main_app.stacked_widget.indexOf(self.main_app.purchase_window) == -1:
            self.main_app.stacked_widget.addWidget(self.main_app.purchase_window)

        # Pass full song data
        self.main_app.purchase_window.load_song_details(song)

        # Switch to purchase window
        self.main_app.stacked_widget.setCurrentWidget(self.main_app.purchase_window)



    # ===================== LOGOUT =====================
    def handle_logout(self):
        self.main_app.session.logout()
        self.main_app.switch_to_login()
