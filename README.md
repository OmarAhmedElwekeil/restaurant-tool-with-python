# 🍽️ Restaurant Management System (PyQt5 + SQLite)

A desktop application for managing restaurant menus, sales, inventory, and insights.  
Built with **Python**, **PyQt5**, and **SQLite**.

---

## 🚀 Features

### 🔑 Authentication
- Login system for admin users.

### 🏠 Admin Home
- **Add / Update Menu Items**
- **View Menu Table**
- **View Sales Table** with total sales calculation.
- **View Customer Comments**
- Navigation to **Insights** page.

### 📊 Insights & Analytics
- **Trending Items** (Top 5 sold)
- **Low Stock Alerts** (Quantity ≤ 3)
- **Inventory Statistics**
  - Average price
  - Most expensive and cheapest item
  - Total inventory value

### 🗄️ Database (`restaurant.db`)
- **users**: Admin credentials.
- **menu**: Items, prices, quantities.
- **sales**: Sold items and prices.
- **comments**: Customer feedback.

---

## 🛠️ Installation

```bash
# 1. Clone this repository
git clone https://github.com/OmarAhmedElwekeil/restaurant-tool-with-python.git
cd restaurant-management

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python main.py
