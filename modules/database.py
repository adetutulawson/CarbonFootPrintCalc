import sqlite3
from contextlib import closing

DATABASE_FILE = r"C:\Users\User\Documents\FinalMSCProject\database\CARBON_FOOTPRINT.db"

def ensure_db():
    with closing(sqlite3.connect(DATABASE_FILE)) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS appliance_data (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    appliance TEXT,
                    appliance_type TEXT,
                    daily_energy REAL,
                    daily_carbon_footprint REAL,
                    change_yesterday REAL,
                    change_last_month REAL,
                    change_last_year REAL,
                    cost REAL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS maintenance_data (
                    id INTEGER PRIMARY KEY,
                    appliance TEXT,
                    last_maintenance_date TEXT
                )
            """)



def save_daily_data(date, appliance, appliance_type, daily_energy, daily_carbon_footprint, change_yesterday, change_last_month, change_last_year, cost):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO appliance_data (
                date, appliance, appliance_type, daily_energy, 
                daily_carbon_footprint, change_yesterday, 
                change_last_month, change_last_year, cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date, appliance, appliance_type, daily_energy, 
            daily_carbon_footprint, change_yesterday, 
            change_last_month, change_last_year, cost
        ))
        conn.commit()

def update_maintenance_date(appliance, date):
    with closing(sqlite3.connect(DATABASE_FILE)) as conn:
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO maintenance_data (appliance, last_maintenance_date) 
                VALUES (?, ?)
            """, (appliance, date))


def read_previous_data(appliance_type=None):
    query = "SELECT * FROM appliance_data"
    params = []
    
    if appliance_type:
        query += " WHERE appliance_type = ?"
        params.append(appliance_type)
    
    query += " ORDER BY date ASC"
    
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]