import sqlite3
import matplotlib.pyplot as plt
from dateutil import parser
from modules.database import get_db_connection

#DATABASE_FILE = "CARBON_FOOTPRINT.db"
# DATABASE_FILE = r"C:\Users\User\Documents\FinalMSCProject\database\CARBON_FOOTPRINT.db"

def fetch_energy_and_carbon_data(appliance_letter):
    query = """
    SELECT Date, Daily_Energy, Daily_Carbon_Footprint 
    FROM appliance_data 
    WHERE Appliance_Type = ?
    ORDER BY Date;
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (appliance_letter,))
        return cursor.fetchall()
    

def visualize_energy_and_carbon(appliance_letter):
    data = fetch_energy_and_carbon_data(appliance_letter)
    
    if not data:
        print("No data available for the selected appliance.")
        return

    dates, energies, carbon_footprints = zip(*[
        (parser.parse(row[0]), float(row[1]), float(row[2])) 
        for row in data if row[1] is not None and row[2] is not None
    ])
    
    plt.figure(figsize=(10, 8))
    plt.plot(dates, energies, marker='o', label='Energy Usage (kWh)', color='blue')
    plt.plot(dates, carbon_footprints, marker='o', label='Carbon Footprint (kg CO2)', color='green')
    
    plt.title(f'{appliance_letter} Energy Usage and Carbon Footprint Over Time')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

def fetch_cost_data(appliance_letter):
    query = """
    SELECT Date, Cost 
    FROM appliance_data 
    WHERE Appliance_Type = ?
    ORDER BY date;
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (appliance_letter,))
        return cursor.fetchall()
    

def visualize_cost_over_time(appliance_letter):
    data = fetch_cost_data(appliance_letter)
    
    if not data:
        print("No data available for the selected appliance.")
        return

    dates, costs = zip(*[
        (parser.parse(row[0]), float(row[1])) 
        for row in data if row[1] is not None
    ])
    
    plt.figure(figsize=(10, 8))
    plt.plot(dates, costs, marker='o', label='Cost (GBP)', color='red')
    
    plt.title(f'{appliance_letter} Cost Over Time')
    plt.xlabel('Date')
    plt.ylabel('Cost (GBP)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


