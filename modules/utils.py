import datetime
import sqlite3
import hashlib

appliance_power_ratings = {
    "Kettle": 3000,
    "Washing Machine": 2100,
    "Hob": 2400,
    "Tumble Dryer": 2500,
    "Microwave": 1000
}


# Usage scenarios (minutes per use, uses per day)
usage_scenarios = {
    "Kettle": {"Light": (2, 3), "Moderate": (5, 4), "Heavy": (7, 6)},
    "Washing Machine": {"Light": (30, 1), "Moderate": (45, 2), "Heavy": (60, 3)},
    "Hob": {"Light": (15, 1), "Moderate": (30, 2), "Heavy": (45, 3)},
    "Tumble Dryer": {"Light": (30, 1), "Moderate": (45, 2), "Heavy": (60, 3)},
    "Microwave": {"Light": (5, 2), "Moderate": (10, 3), "Heavy": (15, 4)}
}

# Benchmark data: Average energy consumption per 10 minutes (in kWh)
benchmark_data = {
    "Kettle": 0.25,
    "Washing Machine": 0.083,
    "Hob": 0.4,
    "Tumble Dryer": 0.5,
    "Microwave": 0.167
}

# Appliance type abbreviations
appliance_abbreviations = {
    "Kettle": "K",
    "Washing Machine": "W",
    "Hob": "H",
    "Tumble Dryer": "T",
    "Microwave": "M"
}

maintenance_intervals = {
    "Kettle": 30,              # e.g., 30 days for Kettle descaling
    "Washing Machine": 90,     # e.g., 90 days for Washing Machine filter cleaning
    "Tumble Dryer": 60,        # e.g., 60 days for Tumble Dryer filter cleaning
    "Microwave": 180,          # e.g., 180 days for Microwave interior cleaning
}

def get_user_choice():
    appliance_names = list(appliance_power_ratings.keys())
    print("Available appliances:")
    for idx, appliance in enumerate(appliance_names, start=1):
        print(f"{idx}. {appliance.title()}")
    try:
        choice = int(input("Select an appliance by entering the corresponding number: ")) - 1
        return appliance_names[choice]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None

def prompt_maintenance_done(appliance):
    response = input(f"Did you perform maintenance on your {appliance.title()}? (yes/no): ").strip().lower()
    return response == "yes"

def get_current_datetime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Add more utility functions as needed...


#Username and Passw0rd
DATABASE_FILE = "CARBON_FOOTPRINT.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    password_hash = hash_password(password)
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash) 
                VALUES (?, ?)
            """, (username, password_hash))
            conn.commit()
            print("User registered successfully.")
    except sqlite3.IntegrityError:
        print("Error: Username already exists.")

def login_user(username, password):
    password_hash = hash_password(password)
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users 
            WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        user = cursor.fetchone()
        if user:
            print("Login successful!")
            return True
        else:
            print("Login failed: Incorrect username or password.")
            return False
