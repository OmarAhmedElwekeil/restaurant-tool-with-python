import sqlite3

def view_all_tables():
    conn = sqlite3.connect("restaurant.db")
    c = conn.cursor()

    tables = ["users", "menu", "cart", "sales", "comments"]

    for table in tables:
        print(f"\n{table} Table")
        try:
            c.execute(f"SELECT * FROM {table}")
            rows = c.fetchall()
            # Get column names
            column_names = [description[0] for description in c.description]
            print("Columns:", column_names)

            if rows:
                for row in rows:
                    print(row)
            else:
                print("No data.")
        except Exception as e:
            print(f"Error reading table {table}: {e}")

    conn.close()

view_all_tables()
