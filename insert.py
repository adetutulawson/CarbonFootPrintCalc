import sqlite3
import csv

DATABASE_FILE = "CARBON_FOOTPRINT.db"
CSV_FILE = "new_appliance_carbon_footprint.csv"  # Replace with your actual CSV file path

def convert_to_float(value):
    try:
        # Try to convert the value to a float
        return float(value)
    except ValueError:
        # If conversion fails, return None
        return None

def insert_csv_to_db(csv_file, db_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Open the CSV file
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        
        # Insert each row into the database
        for row in reader:
            cursor.execute("""
                INSERT INTO appliance_data (Date, Appliance, Appliance_Type, Daily_Energy, Daily_Carbon_Footprint, 
                Change_Yesterday, Change_Last_Month, Change_Last_Year, Cost) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["Date"],
                row["Appliance"],
                row["Appliance_Type"],
                convert_to_float(row["Daily Energy (kWh)"]),
                convert_to_float(row["Daily Carbon Footprint (kg CO2)"]),
                convert_to_float(row["Change from Yesterday (kg CO2)"]),
                convert_to_float(row["Change from Last Month (kg CO2)"]),
                convert_to_float(row["Change from Last Year (kg CO2)"]),
                convert_to_float(row["Cost (GBP)"])
            ))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    print("CSV data has been successfully inserted into the database.")

if __name__ == "__main__":
    insert_csv_to_db(CSV_FILE, DATABASE_FILE)
