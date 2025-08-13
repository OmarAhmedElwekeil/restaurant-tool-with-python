import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QListWidget, QFrame, QMessageBox, QListWidgetItem
)
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt
import sqlite3
from logging import LoggingWindow


class AdminHome(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Admin Home")
        self.setFixedSize(1400, 900)

        # Background setup
        self.setAutoFillBackground(True)
        palette = QPalette()
        pixmap = QPixmap("bg.jpg").scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # --- Add Item Section
        add_layout = QVBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Item Name")

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Item Price")

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Item Quantity")

        add_button = QPushButton("Add Item")
        add_button.clicked.connect(self.add_item)
        add_button.setStyleSheet("background-color: white; color: black; font-weight: bold;")

        add_layout.addWidget(self.name_input)
        add_layout.addWidget(self.price_input)
        add_layout.addWidget(self.quantity_input)
        add_layout.addWidget(add_button)

        # Menu Table
        menu_label = QLabel("Menu")
        menu_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.menu_table = QTableWidget()
        self.menu_table.setColumnCount(3)
        self.menu_table.setHorizontalHeaderLabels(["Item", "Price", "Quantity"])
        self.menu_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 140);
            }
            QHeaderView::section {
                background-color: grey;
                font-weight: bold;
            }
        """)

        left_layout.addLayout(add_layout)
        left_layout.addWidget(menu_label)
        left_layout.addWidget(self.menu_table)
        self.load_menu_items()

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("color: white;")
        separator.setLineWidth(2)

        # Sales Table
        sales_label = QLabel("Sales")
        sales_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(3)
        self.sales_table.setHorizontalHeaderLabels(["Item", "Price", "Quantity"])
        self.sales_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 140);
            }
            QHeaderView::section {
                background-color: grey;
                font-weight: bold;
            }
        """)

        self.total_label = QLabel("Total Sales: $0.00")
        self.total_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")

        # Comments
        comments_label = QLabel("Customer Comments")
        comments_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.comments_list = QListWidget()
        self.comments_list.setFixedHeight(150)
        self.comments_list.setStyleSheet("background-color: rgba(255, 255, 255, 140);")
        self.load_comments()

        # Right Layout
        right_layout.addWidget(sales_label)
        right_layout.addWidget(self.sales_table)
        right_layout.addWidget(self.total_label)
        right_layout.addWidget(comments_label)
        right_layout.addWidget(self.comments_list)

        button_layout = QHBoxLayout()

        show_insights_btn = QPushButton("Show Insights")
        show_insights_btn.setStyleSheet("background-color: white; color: black; font-weight: bold; padding: 6px;")
        show_insights_btn.setFixedWidth(120)
        show_insights_btn.clicked.connect(self.open_insights)

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("background-color: white; color: black; font-weight: bold; padding: 6px;")
        logout_btn.setFixedWidth(100)
        logout_btn.clicked.connect(self.logout)

        button_layout.addWidget(show_insights_btn)
        button_layout.addWidget(logout_btn)
        button_layout.setAlignment(Qt.AlignRight)

        right_layout.addLayout(button_layout)

        # Main Layout
        main_layout.addLayout(left_layout)
        main_layout.addWidget(separator)
        main_layout.addLayout(right_layout)

        # Welcome Label
        self.welcome_label = QLabel(f"Welcome, {self.username}")
        self.welcome_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.welcome_label.setStyleSheet("color: white;")
        self.welcome_label.setAlignment(Qt.AlignCenter)

        final_layout = QVBoxLayout()
        final_layout.addWidget(self.welcome_label)
        final_layout.addLayout(main_layout)

        self.setLayout(final_layout)

        # Final data load
        self.update_sales_table()

    def get_menu(self):
        conn = sqlite3.connect("restaurant.db")
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

    def add_item(self):
        item_name = self.name_input.text().strip()
        try:
            price = float(self.price_input.text().strip())
            quantity = int(self.quantity_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Price must be a number and quantity must be an integer.")
            return

        if not item_name:
            QMessageBox.warning(self, "Input Error", "Item name cannot be empty.")
            return

        with sqlite3.connect("restaurant.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT price, quantity FROM menu WHERE LOWER(item_name) = LOWER(?)", (item_name,))
            result = cursor.fetchone()

            if result:
                cursor.execute("""
                    UPDATE menu
                    SET price    = ?,
                        quantity = quantity + ?
                    WHERE LOWER(item_name) = LOWER(?)
                """, (price, quantity, item_name))
            else:
                cursor.execute("""
                    INSERT INTO menu (item_name, price, quantity)
                    VALUES (?, ?, ?)
                """, (item_name, price, quantity))

            conn.commit()

        self.load_menu_items()
        self.name_input.clear()
        self.price_input.clear()
        self.quantity_input.clear()
        QMessageBox.information(self, "Success", "Item added or updated successfully.")

    def get_sales(self):
        conn = sqlite3.connect("restaurant.db")
        c = conn.cursor()
        c.execute("SELECT item_name, price, quantity FROM sales")
        sales = c.fetchall()
        conn.close()
        return sales

    def get_total_sales(self):
        conn = sqlite3.connect("restaurant.db")
        c = conn.cursor()
        c.execute("SELECT SUM(price * quantity) FROM sales")
        total = c.fetchone()[0]
        conn.close()
        return total or 0.0

    def update_sales_table(self):
        sales = self.get_sales()
        self.sales_table.setRowCount(len(sales))
        for row_idx, (item, price, quantity) in enumerate(sales):
            self.sales_table.setItem(row_idx, 0, QTableWidgetItem(str(item)))
            self.sales_table.setItem(row_idx, 1, QTableWidgetItem(f"${price:.2f}"))
            self.sales_table.setItem(row_idx, 2, QTableWidgetItem(str(quantity)))
        total = self.get_total_sales()
        self.total_label.setText(f"Total Sales: ${total:.2f}")

    def load_comments(self):
        comments = self.get_comments()
        for comment in comments:
            item = QListWidgetItem(comment)
            self.comments_list.addItem(item)

    def get_comments(self):
        conn = sqlite3.connect("restaurant.db")
        c = conn.cursor()
        c.execute("SELECT comment FROM comments")
        comments = [row[0] for row in c.fetchall()]
        conn.close()
        return comments

    def open_insights(self):
        from features import InsightsPage
        self.insights_window = InsightsPage(self.username)
        self.insights_window.show()
        self.close()

    def logout(self):
        self.login_window = LoggingWindow()
        self.login_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminHome("admin_user")  # Test with fake username
    window.show()
    sys.exit(app.exec_())
