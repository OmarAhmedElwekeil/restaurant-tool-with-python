import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFrame, QListWidgetItem
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import sqlite3


class InsightsPage(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setFixedSize(1400, 900)
        self.setWindowTitle("Restaurant Insights")
        self.setStyleSheet("color: white; font-size: 18px;")

        # Background image
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap("bg.jpg").scaled(self.size(), Qt.KeepAspectRatioByExpanding))
        self.bg_label.setGeometry(0, 0, 1400, 900)
        self.bg_label.lower()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Top bar with Back button
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        back_button = QPushButton("⬅️ Back to Admin")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                padding: 10px 20px;
                border-radius: 10px;
                color: white;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        back_button.clicked.connect(self.go_back_to_admin)
        top_bar.addWidget(back_button)
        layout.addLayout(top_bar)

        # Title
        title = QLabel(f"📊 Restaurant Insights (User: {self.username})")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        sections_layout = QHBoxLayout()
        layout.addLayout(sections_layout)

        trending_box = self.create_list_section("🔥 Trending Items", self.get_trending_items())
        sections_layout.addWidget(trending_box)

        stock_box = self.create_list_section("⚠️ Low Stock Items", self.get_low_stock_items())
        sections_layout.addWidget(stock_box)

        stats_box = self.create_stats_section()
        sections_layout.addWidget(stats_box)

    def go_back_to_admin(self):
        from admin import AdminHome
        self.admin_page = AdminHome(self.username)
        self.admin_page.show()
        self.close()

    def create_list_section(self, title, items):
        box = QVBoxLayout()
        label = QLabel(title)
        label.setFont(QFont("Arial", 20, QFont.Bold))
        box.addWidget(label)
        list_widget = QListWidget()
        list_widget.setStyleSheet("background-color: rgba(255, 255, 255, 0.2);")
        for item in items:
            list_widget.addItem(QListWidgetItem(item))
        box.addWidget(list_widget)
        frame = QFrame()
        frame.setLayout(box)
        frame.setStyleSheet("background-color: rgba(0, 0, 0, 0.3); padding: 10px; border-radius: 15px;")
        return frame

    def create_stats_section(self):
        box = QVBoxLayout()
        label = QLabel("📦 Inventory Insights")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        box.addWidget(label)
        stats = self.get_inventory_stats()
        for stat in stats:
            stat_label = QLabel(stat)
            stat_label.setFont(QFont("Arial", 16))
            box.addWidget(stat_label)
        frame = QFrame()
        frame.setLayout(box)
        frame.setStyleSheet("background-color: rgba(0, 0, 0, 0.3); padding: 10px; border-radius: 15px;")
        return frame

    def get_trending_items(self):
        conn = sqlite3.connect("restaurant.db")
        c = conn.cursor()
        c.execute('''
            SELECT item_name, SUM(quantity) as total_qty 
            FROM sales 
            GROUP BY item_name 
            ORDER BY total_qty DESC 
            LIMIT 5
        ''')
        results = [f"{row[0]} - {row[1]} sold" for row in c.fetchall()]
        conn.close()
        return results or ["No sales data available"]

    def get_low_stock_items(self):
        conn = sqlite3.connect("restaurant.db")
        c = conn.cursor()
        c.execute('SELECT item_name, quantity FROM menu WHERE quantity <= 3')
        results = [f"{row[0]} - Only {row[1]} left" for row in c.fetchall()]
        conn.close()
        return results or ["No items with low stock"]

    def get_inventory_stats(self):
        conn = sqlite3.connect("restaurant.db")
        c = conn.cursor()
        try:
            c.execute('SELECT AVG(price) FROM menu')
            avg_price = round(c.fetchone()[0] or 0, 2)
            c.execute('SELECT item_name, price FROM menu ORDER BY price DESC LIMIT 1')
            most_expensive = c.fetchone() or ("N/A", 0)
            c.execute('SELECT item_name, price FROM menu ORDER BY price ASC LIMIT 1')
            cheapest = c.fetchone() or ("N/A", 0)
            c.execute('SELECT SUM(price * quantity) FROM menu')
            total_value = round(c.fetchone()[0] or 0, 2)
        except:
            avg_price, most_expensive, cheapest, total_value = 0, ("N/A", 0), ("N/A", 0), 0
        conn.close()
        return [
            f"🔹 Average Price: {avg_price} EGP",
            f"💎 Most Expensive: {most_expensive[0]} - {most_expensive[1]} EGP",
            f"🥉 Cheapest: {cheapest[0]} - {cheapest[1]} EGP",
            f"💰 Total Inventory Value: {total_value} EGP"
        ]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InsightsPage("admin_user")  # Test username
    window.show()
    sys.exit(app.exec_())
