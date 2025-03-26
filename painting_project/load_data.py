import pandas as pd
import mysql.connector

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mumma93322",
    database="painting_db"
)
cursor = conn.cursor()

# File paths
csv_files = {
    "artist": "cleaned_artist.csv",
    "canvas_size": "cleaned_canvas_size.csv",
    "image_link": "cleaned_image_link.csv",
    "museum": "cleaned_museum.csv",
    "museum_hours": "cleaned_museum_hours.csv",
    "product_size": "cleaned_product_size.csv",
    "subject": "cleaned_subject.csv",
    "work": "cleaned_work.csv"
}

# Load data function
def load_data(table, file):
    df = pd.read_csv(file)
    columns = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    for _, row in df.iterrows():
        cursor.execute(query, tuple(row))
    conn.commit()

# Insert data into MySQL
for table, file in csv_files.items():
    load_data(table, file)

print("Data successfully inserted!")

cursor.close()
conn.close()
