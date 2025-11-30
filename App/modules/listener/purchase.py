from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6 import uic

class PurchaseWindow(QDialog):
    def __init__(self, main_app):
        super().__init__()
        uic.loadUi("ui/purchase.ui", self)
        self.main_app = main_app

        self.song_data = None

        # Make line edits read-only safely
        if hasattr(self, "artistNameLine"):
            self.artistNameLine.setReadOnly(True)
        if hasattr(self, "songLineEdit"):
            self.songLineEdit.setReadOnly(True)
        if hasattr(self, "priceLineEdit"):
            self.priceLineEdit.setReadOnly(True)

        # Connect buttons
        self.proceedButton.clicked.connect(self.go_to_checkout)
        self.backButton.clicked.connect(self.go_back)

    def load_song_details(self, song_data):
        """
        song_data = {
            "songID": ...,
            "artist": ...,
            "song": ...,
            "price": ...
        }
        """
        self.song_data = song_data
        self.artistNameLine.setText(song_data.get("artistName") or song_data.get("artist", "Unknown"))
        self.songLineEdit.setText(song_data.get("songName") or song_data.get("song", "Unknown"))

        self.priceLineEdit.setText(str(song_data.get("price", 0.00)))

        # Clear old input fields
        self.creditCardLineEdit.clear()
        self.expiryLineEdit.clear()

    def go_back(self):
        """Return to search screen."""
        self.main_app.stacked_widget.setCurrentWidget(self.main_app.search_window)

    def go_to_checkout(self):
        card = self.creditCardLineEdit.text().strip()
        expiry = self.expiryLineEdit.text().strip()

        if not card or not expiry:
            QMessageBox.warning(self, "Missing Info", "Please enter credit card and expiry date.")
            return

        # Create checkout window if it doesn't exist
        if not hasattr(self.main_app, "checkout_window") or not self.main_app.checkout_window:
            from modules.listener.checkout import CheckoutWindow
            self.main_app.checkout_window = CheckoutWindow(self.main_app)

        # ✅ Ensure checkout_window is in stacked widget
        if self.main_app.stacked_widget.indexOf(self.main_app.checkout_window) == -1:
            self.main_app.stacked_widget.addWidget(self.main_app.checkout_window)

        # Pass the full song dictionary
        self.main_app.checkout_window.load_checkout_details(
            song_data=self.song_data,
            credit_card=card,
            expiry=expiry
        )

        # Switch to checkout screen
        self.main_app.stacked_widget.setCurrentWidget(self.main_app.checkout_window)
