from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QFrame, QMessageBox
)
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt, QEvent
import sys
from logging import LoggingWindow
import sqlite3

DB_PATH = "restaurant.db"

class CustomerHome(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Customer Home")
        self.setGeometry(100, 100, 1400, 900)
        self.setFixedSize(1400, 900)

        self.set_background("bg.jpg")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.welcome_label = QLabel(f"Welcome, {self.username}")
        self.welcome_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.welcome_label.setStyleSheet("color: white;")
        self.welcome_label.setAlignment(Qt.AlignCenter)

        # Menu Table
        self.menu_table = QTableWidget(0, 3)
        self.menu_table.setHorizontalHeaderLabels(["Item", "Price", "Quantity"])
        self.menu_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 150);
                color: black;
                gridline-color: gray;
            }
            QHeaderView::section {
                background-color: #CCCCCC;
                color: black;
                font-weight: bold;
            }
        """)
        self.menu_table.verticalHeader().setVisible(False)
        self.load_menu_items()

        # Add to Cart button
        self.add_to_cart_btn = QPushButton("Add to Cart")
        self.add_to_cart_btn.clicked.connect(self.handle_add_to_cart)

        # Cart Table
        self.cart_table = QTableWidget(0, 3)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Price", "Quantity"])
        self.cart_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 150);
                color: black;
                gridline-color: gray;
            }
            QHeaderView::section {
                background-color: #CCCCCC;
                color: black;
                font-weight: bold;
            }
        """)
        self.cart_table.verticalHeader().setVisible(False)

        # Buttons and labels
        self.delete_btn = QPushButton("Delete from Cart")
        self.delete_btn.clicked.connect(self.handle_delete_from_cart)

        self.confirm_btn = QPushButton("Confirm Order")
        self.confirm_btn.clicked.connect(self.handle_confirm_order)

        self.logout_btn = QPushButton("Log Out")
        self.logout_btn.clicked.connect(self.logout)

        self.total_label = QLabel("Total = $0")
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.total_label.setStyleSheet("color: white;")

        # Comment box
        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Set your comment here...")
        self.comment_input.setFixedHeight(70)
        self.comment_input.installEventFilter(self)

        # Layouts
        right_layout = QVBoxLayout()
        cart_label = QLabel("Your Cart")
        cart_label.setStyleSheet("color: white; font-weight: bold;")
        right_layout.addWidget(cart_label)
        right_layout.addWidget(self.cart_table)
        right_layout.addWidget(self.delete_btn)
        right_layout.addWidget(self.total_label)
        right_layout.addWidget(self.confirm_btn)
        right_layout.addWidget(self.comment_input)
        right_layout.addWidget(self.logout_btn, alignment=Qt.AlignRight)

        menu_layout = QVBoxLayout()
        menu_label = QLabel("Menu")
        menu_label.setStyleSheet("color: white; font-weight: bold;")
        menu_layout.addWidget(menu_label)
        menu_layout.addWidget(self.menu_table)
        menu_layout.addWidget(self.add_to_cart_btn)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setLineWidth(2)

        tables_layout = QHBoxLayout()
        tables_layout.addLayout(menu_layout, 2)
        tables_layout.addWidget(separator)
        tables_layout.addLayout(right_layout, 3)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.welcome_label)
        main_layout.addLayout(tables_layout)

        central_widget.setLayout(main_layout)

        self.refresh_cart_table()

    def set_background(self, image_path):
        background = QPixmap(image_path)
        if background.isNull():
            print("Background image not found.")
            return
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self.setPalette(palette)

    def get_menu(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT item_name, price, quantity FROM menu")
        items = c.fetchall()
        conn.close()
        return items

    def load_menu_items(self):
        items = self.get_menu()
        self.menu_table.setRowCount(len(items))
        for row_idx, (name, price, quantity) in enumerate(items):
            self.menu_table.setItem(row_idx, 0, QTableWidgetItem(str(name)))
            self.menu_table.setItem(row_idx, 1, QTableWidgetItem(str(price)))
            self.menu_table.setItem(row_idx, 2, QTableWidgetItem(str(quantity)))

    def handle_add_to_cart(self):
        selected = self.menu_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to add.")
            return
        item_name = self.menu_table.item(selected, 0).text()
        self.add_to_cart(self.username, item_name)
        self.load_menu_items()
        self.refresh_cart_table()

    def handle_delete_from_cart(self):
        selected = self.cart_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to delete.")
            return
        item_name = self.cart_table.item(selected, 0).text()
        self.delete_from_cart(self.username, item_name)
        self.load_menu_items()
        self.refresh_cart_table()

    def handle_confirm_order(self):
        self.confirm_order(self.username)
        QMessageBox.information(self, "Order Confirmed", "Your order has been placed!")
        self.refresh_cart_table()
        self.load_menu_items()

    def refresh_cart_table(self):
        cart = self.get_cart(self.username)
        self.cart_table.setRowCount(len(cart))
        for row_idx, (item_name, quantity, price) in enumerate(cart):
            self.cart_table.setItem(row_idx, 0, QTableWidgetItem(item_name))
            self.cart_table.setItem(row_idx, 1, QTableWidgetItem(str(price)))
            self.cart_table.setItem(row_idx, 2, QTableWidgetItem(str(quantity)))
        total = self.calculate_total(self.username)
        self.total_label.setText(f"Total = ${total}")

    def add_to_cart(self, username, item_name):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT price, quantity FROM menu WHERE item_name = ?", (item_name,))
            item = cursor.fetchone()
            if item and item[1] > 0:
                price = item[0]
                cursor.execute("SELECT quantity FROM cart WHERE username = ? AND item_name = ?", (username, item_name))
                cart_item = cursor.fetchone()
                if cart_item:
                    new_qty = cart_item[0] + 1
                    cursor.execute("UPDATE cart SET quantity = ? WHERE username = ? AND item_name = ?",
                                   (new_qty, username, item_name))
                else:
                    cursor.execute("INSERT INTO cart (username, item_name, price, quantity) VALUES (?, ?, ?, ?)",
                                   (username, item_name, price, 1))
                cursor.execute("UPDATE menu SET quantity = quantity - 1 WHERE item_name = ?", (item_name,))
                conn.commit()

    def get_cart(self, username):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT item_name, quantity, price FROM cart WHERE username = ?", (username,))
            return cursor.fetchall()

    def delete_from_cart(self, username, item_name):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM cart WHERE username = ? AND item_name = ?", (username, item_name))
            item = cursor.fetchone()
            if item:
                qty_to_restore = item[0]
                cursor.execute("DELETE FROM cart WHERE username = ? AND item_name = ?", (username, item_name))
                cursor.execute("UPDATE menu SET quantity = quantity + ? WHERE item_name = ?",
                               (qty_to_restore, item_name))
                conn.commit()

    def calculate_total(self, username):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT price, quantity FROM cart WHERE username = ?", (username,))
            items = cursor.fetchall()
            return sum(price * qty for price, qty in items)

    def confirm_order(self, username):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT item_name, price, quantity FROM cart WHERE username = ?", (username,))
            cart_items = cursor.fetchall()
            for item_name, price, quantity in cart_items:
                cursor.execute("INSERT INTO sales (username, item_name, price, quantity) VALUES (?, ?, ?, ?)",
                               (username, item_name, price, quantity))
            cursor.execute("DELETE FROM cart WHERE username = ?", (username,))
            conn.commit()

    def eventFilter(self, obj, event):
        if obj == self.comment_input and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                comment = self.comment_input.toPlainText().strip()
                if comment:
                    self.save_comment_to_db(comment)
                    self.comment_input.clear()
                    QMessageBox.information(self, "Thank you!", "Your comment has been saved.")
                else:
                    QMessageBox.warning(self, "Empty", "Please enter a comment before submitting.")
                return True
        return super().eventFilter(obj, event)

    def save_comment_to_db(self, comment):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO comments (comment) VALUES (?)", (comment,))
            conn.commit()

    def logout(self):
        self.login_window = LoggingWindow()
        self.login_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomerHome()
    window.show()
    sys.exit(app.exec_())

