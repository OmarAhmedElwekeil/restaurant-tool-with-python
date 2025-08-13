import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QComboBox, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont
from PyQt5.QtCore import Qt
import sqlite3


class LoggingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1400, 900)
        self.setWindowTitle("Restaurant Login")

        self.setup_background()
        self.setup_ui()

    def setup_background(self):
        # Load and apply background image
        bg_path = "bg.jpg"
        if os.path.exists(bg_path):
            pixmap = QPixmap(bg_path).scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(pixmap))
            self.setPalette(palette)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Welcome to our restaurant")
        title.setFont(QFont("serif", 26, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Name")
        self.name_input.setFixedWidth(300)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Enter Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFixedWidth(300)

        self.role_box = QComboBox()
        self.role_box.addItems(["Customer", "Admin"])
        self.role_box.setFixedWidth(300)

        btn_layout = QHBoxLayout()
        login_btn = QPushButton("Sign In")
        signup_btn = QPushButton("Sign Up")
        login_btn.clicked.connect(self.sign_in)
        signup_btn.clicked.connect(self.sign_up)
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(signup_btn)

        for widget in [self.name_input, self.pass_input, self.role_box]:
            layout.addWidget(widget)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def sign_in(self):
        username = self.name_input.text().strip()
        password = self.pass_input.text()
        role = self.role_box.currentText()

        conn = sqlite3.connect("restaurant.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?", (username, password, role))
        result = c.fetchone()
        conn.close()

        if result:
            QMessageBox.information(self, "Success", f"Signed in as {role}")

            import importlib

            if role.lower() == "admin":
                admin_module = importlib.import_module("admin")
                self.admin_window = admin_module.AdminHome(username)
                self.admin_window.show()
            else:
                customer_module = importlib.import_module("customer_page")
                self.customer_window = customer_module.CustomerHome(username)
                self.customer_window.show()

            self.close()

        else:
            QMessageBox.warning(self, "Error", "Invalid credentials or user not found.")

    def sign_up(self):
        username = self.name_input.text().strip()
        password = self.pass_input.text()
        role = self.role_box.currentText()

        conn = sqlite3.connect("restaurant.db")
        c = conn.cursor()

        # Check if user already exists
        c.execute("SELECT * FROM users WHERE username = ? AND role = ?", (username, role))
        if c.fetchone():
            QMessageBox.warning(self, "Exists", "User already exists. Please sign in.")
        else:
            # Insert new user
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            QMessageBox.information(self, "Success", "User signed up successfully. You can now sign in.")

        conn.close()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoggingWindow()
    window.show()
    sys.exit(app.exec_())
