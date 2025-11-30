from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6 import uic
from datetime import datetime

class CheckoutWindow(QMainWindow):
    def __init__(self, main_app):
        super().__init__()
        uic.loadUi("ui/checkout.ui", self)
        self.main_app = main_app

        # Data placeholders
        self.song_data = None  # Full song dict including songID
        self.card = None
        self.expiry = None

        # Connect buttons
        self.backButton.clicked.connect(self.go_back)
        self.purchaseButton.clicked.connect(self.finalize_purchase)

        # Make line edits read-only
        self.artistLine.setReadOnly(True)
        self.songLine.setReadOnly(True)
        self.billLine.setReadOnly(True)

    def load_checkout_details(self, song_data, credit_card="", expiry=""):
        """Load song and payment info from Purchase Screen."""
        self.song_data = song_data  # ✅ full dict with songID
        self.card = credit_card
        self.expiry = expiry
        self.artistLine.setText(song_data.get("artistName") or song_data.get("artist", "Unknown"))
        self.songLine.setText(song_data.get("songName") or song_data.get("song", "Unknown"))
        self.billLine.setText(f"${song_data.get('price', 0.00):.2f}")

    def go_back(self):
        """Return to Purchase Screen."""
        self.main_app.stacked_widget.setCurrentWidget(self.main_app.purchase_window)

    def finalize_purchase(self):
        """Save purchase in DB, show success popup, update search window, and return to search."""
        listener_id = getattr(self.main_app.session, "current_user", None)
        if not listener_id:
            QMessageBox.critical(self, "Error", "No logged-in listener.")
            return

        if not self.song_data:
            QMessageBox.critical(self, "Error", "No song selected for purchase.")
            return

        db = getattr(self.main_app, "db", None)
        if not db:
            QMessageBox.critical(self, "Error", "Database connection not found.")
            return

        try:
            # Convert expiry MM/YY to proper date for SQL Server
            try:
                month, year = self.expiry.split('/')
                year_full = int(year)
                if year_full < 100:
                    year_full += 2000  # e.g., '22' -> 2022
                expiry_date = datetime(year_full, int(month), 1).date()
            except Exception:
                QMessageBox.warning(self, "Invalid Expiry", "Expiry must be in MM/YY format.")
                return

            # Insert purchase into DB (do not specify identity column)
            query = """
                INSERT INTO Purchase (songID, HUID, creditCardNum, expiryDate)
                VALUES (?, ?, ?, ?)
            """
            params = (
                self.song_data.get("songID"),
                listener_id,
                self.card,
                expiry_date,
            )

            cursor = db.connection.cursor()
            cursor.execute(query, params)
            db.connection.commit()
            print("DEBUG: Purchase committed successfully:", params)

            # Update selected_song in search window
            if (self.main_app.search_window.selected_song and
                self.main_app.search_window.selected_song["songID"] == self.song_data.get("songID")):
                self.main_app.search_window.selected_song["purchased"] = True

            # Reload purchased songs list
            self.main_app.search_window.load_purchased_songs()

            # Show success popup
            QMessageBox.information(self, "Success", " Song purchased successfully!")

            # Switch back to search & play screen
            self.main_app.stacked_widget.setCurrentWidget(self.main_app.search_window)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error: {e}")
