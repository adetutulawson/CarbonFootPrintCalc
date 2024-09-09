from modules.appliances import handle_appliance_scenario, check_maintenance_reminder,appliance_power_ratings, visualize_cost_over_time,calculate_carbon_footprint,calculate_changes, calculate_energy_consumption, calculate_energy_cost
from modules.appliances import calculate_energy_consumption,calculate_changes, DEFAULT_CUP_VOLUME_ML, calculate_energy_for_cup_of_tea,calculate_energy_for_heating_water, ROOM_TEMPERATURE,BOILING_POINT, DEFAULT_Kettle_EFFICIENCY
from modules.database import ensure_db, save_daily_data, update_maintenance_date,sqlite3
from modules.calculations import CO2_EMISSION_FACTOR_UK,ELECTRICITY_RATE_PER_KWH, calculate_energy_cost
from modules.utils import  maintenance_intervals, usage_scenarios, appliance_abbreviations,appliance_power_ratings, benchmark_data, datetime, register_user, login_user
from modules.visualisation import visualize_cost_over_time, visualize_energy_and_carbon

def main():
    #ensure_csv_headers()
    
    #print("Welcome to your Appliances Carbon Footprint Estimator!")
    #print("Available appliances:")

    print("Welcome to the Appliance Carbon Footprint Estimator!")
    choice = input("Do you have an account? (yes/no): ").strip().lower()
    
    if choice == 'no':
        print("Let's create a new account for you.")
        username = input("Enter a username: ").strip()
        password = input("Enter a password: ").strip()
        register_user(username, password)
    
    print("Please log in to continue.")
    while True:
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        if login_user(username, password):
            break
        else:
            print("Please try again.")
    
    # Proceed to the rest of your application
    handle_Kettle_scenario()

    
    appliance_names = list(appliance_power_ratings.keys())
    for idx, appliance in enumerate(appliance_names, start=1):
        print(f"{idx}. {appliance.title()}")

    try:
        appliance_choice = int(input("Select an appliance by entering the corresponding number: ")) - 1
        selected_appliance = appliance_names[appliance_choice]
    except (ValueError, IndexError):
        print("Invalid selection. Exiting.")
        return

    # Special handling for Kettle
    if selected_appliance == "Kettle":
        handle_Kettle_scenario()
    elif selected_appliance == "Washing Machine":
        handle_washing_machine_scenario()
    else:
        handle_general_appliance_scenario(selected_appliance)

    # Ask if maintenance was performed
    if selected_appliance in maintenance_intervals:
        maintenance_done = input(f"Did you perform maintenance on your {selected_appliance.title()}? (yes/no): ").strip().lower()
        if maintenance_done == "yes":
            update_maintenance_date(selected_appliance)

# Updated handle_general_appliance_scenario to include cost calculation
def handle_general_appliance_scenario(appliance):
    print(f"\n{appliance.title()} Usage Scenario")
    
    print("Available usage scenarios:")
    scenarios = list(usage_scenarios[appliance].keys())
    for idx, scenario in enumerate(scenarios, start=1):
        print(f"{idx}. {scenario}")

    try:
        scenario_choice = int(input("Select a usage scenario by entering the corresponding number: ")) - 1
        scenario = scenarios[scenario_choice]
        usage_time_minutes, uses_per_day = usage_scenarios[appliance][scenario]
    except (ValueError, IndexError):
        print("Invalid selection. Exiting.")
        return

    power_rating_watts = appliance_power_ratings[appliance]
    daily_energy = calculate_energy_consumption(power_rating_watts, usage_time_minutes, uses_per_day)
    daily_carbon_footprint = calculate_carbon_footprint(daily_energy, CO2_EMISSION_FACTOR_UK)
    cost = calculate_energy_cost(daily_energy, ELECTRICITY_RATE_PER_KWH)

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate changes
    change_yesterday, change_last_month, change_last_year = calculate_changes(appliance, now, daily_carbon_footprint)

    appliance_type = appliance_abbreviations[appliance]
    save_daily_data(date_str, appliance, appliance_type, daily_energy, daily_carbon_footprint, change_yesterday, change_last_month, change_last_year, cost)

    print(f"\nEnergy Consumption for {appliance.title()} (kWh): {daily_energy:.2f}")
    print(f"Carbon Footprint for {appliance.title()} (kg CO2): {daily_carbon_footprint:.2f}")
    print(f"Change from Yesterday (kg CO2): {round(change_yesterday, 2) if change_yesterday is not None else 'N/A'}")
    print(f"Change from Last Month (kg CO2): {round(change_last_month, 2) if change_last_month is not None else 'N/A'}")
    print(f"Change from Last Year (kg CO2): {round(change_last_year, 2) if change_last_year is not None else 'N/A'}")
    print(f"Cost for {appliance.title()} (GBP): £{round(cost, 2)}")

    # High Usage Alert
    #check_high_usage_alert(appliance, daily_energy)

    # Benchmark comparison
    #compare_with_benchmark(appliance, daily_energy)

def display_energy_saving_tips(appliance):
    print("\nEnergy-Saving Tips:")
    if appliance == "Kettle":
        print("- Consider boiling only the amount of water you need.")
        print("- Use a Kettle with a higher efficiency rating.")
        print("- If you frequently make tea, consider using a thermos to keep water hot longer, reducing the need to reboil.")
    elif appliance == "Washing Machine":
        print("- Use cold water for washing clothes whenever possible.")
        print("- Make sure to run full loads to maximize energy efficiency.")
        print("- Use the eco-wash cycle to save energy.")
    # Add more tips for other appliances as needed


def compare_with_benchmark(appliance, daily_energy, specific_volume):
    benchmark_energy_kwh = benchmark_data[appliance]

    # Assuming 1.7L is the full Kettle volume for the benchmark
    full_Kettle_volume = 1.7  # liters
    usage_time_minutes = 5  # Assuming it takes 5 minutes to boil 1.7L

    # Calculate the energy for boiling the specific volume
    energy_for_specific_volume = benchmark_energy_kwh * (specific_volume / full_Kettle_volume)

    print(f"\nBenchmark Comparison for {appliance.title()}:")
    if daily_energy > energy_for_specific_volume:
        print(f"Your daily energy consumption ({round(daily_energy, 2)} kWh) is above the benchmark ({round(energy_for_specific_volume, 2)} kWh) for boiling {specific_volume} liters.")
        display_energy_saving_tips(appliance)
    else:
        print(f"Great job! Your daily energy consumption ({round(daily_energy, 2)} kWh) is below the benchmark ({round(energy_for_specific_volume, 2)} kWh) for boiling {specific_volume} liters.")
        print("Keep up the good work in managing your energy usage efficiently!")

def handle_Kettle_scenario():
    print("Kettle Usage Scenario")
    
    try:
        number_of_cups = int(input("Enter the number of cups of tea you intend to make: "))
        if number_of_cups <= 0:
            raise ValueError("The number of cups must be a positive integer.")
    except ValueError as e:
        print(e)
        return

    try:
        custom_cup_size = input(f"Enter the cup size in ml (press enter to use default {DEFAULT_CUP_VOLUME_ML} ml): ")
        cup_size_ml = float(custom_cup_size) if custom_cup_size else DEFAULT_CUP_VOLUME_ML
    except ValueError:
        print("Invalid input. Using default cup size.")
        cup_size_ml = DEFAULT_CUP_VOLUME_ML
    
    # Calculate total volume of water to be boiled
    total_volume_liters = (cup_size_ml * number_of_cups) / 1000  # Convert ml to liters

    # Calculate the energy consumption for boiling the specific volume of water
    total_energy_kwh = calculate_energy_for_cup_of_tea(cup_size_ml, ROOM_TEMPERATURE, BOILING_POINT, DEFAULT_Kettle_EFFICIENCY) * number_of_cups
    #total_carbon_footprint = calculate_carbon_footprint(total_energy_kwh, CO2_EMISSION_FACTOR_UK)
    total_carbon_footprint = calculate_carbon_footprint(total_energy_kwh)
    #cost = calculate_energy_cost(total_energy_kwh, ELECTRICITY_RATE_PER_KWH)
    cost = calculate_energy_cost(total_energy_kwh)

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate changes
    change_yesterday, change_last_month, change_last_year = calculate_changes("Kettle", now, total_carbon_footprint)

    # Compare the user's energy consumption with the benchmark
    compare_with_benchmark("Kettle", total_energy_kwh)  # Only pass two arguments if the function accepts two

    # Save the data to the CSV
    save_daily_data(date_str, "Kettle", "K", total_energy_kwh, total_carbon_footprint, change_yesterday, change_last_month, change_last_year, cost)

    # Display results
    print(f"\nEnergy Consumption for {number_of_cups} cup(s) of tea (kWh): {total_energy_kwh:.2f}")
    print(f"Carbon Footprint for {number_of_cups} cup(s) of tea (kg CO2): {total_carbon_footprint:.2f}")
    print(f"Change from Yesterday (kg CO2): {round(change_yesterday, 2) if change_yesterday is not None else 'N/A'}")
    print(f"Change from Last Month (kg CO2): {round(change_last_month, 2) if change_last_month is not None else 'N/A'}")
    print(f"Change from Last Year (kg CO2): {round(change_last_year, 2) if change_last_year is not None else 'N/A'}")
    print(f"Cost for boiling {number_of_cups} cup(s) of tea (GBP): £{round(cost, 2)}")
    
    visualize_energy_and_carbon("K")  # For Kettle's energy and carbon footprint
    visualize_cost_over_time("K") 
    cumulative_impact(total_energy_kwh, total_carbon_footprint)
      # Automatically generate and display the usage visualization
   # visualize_usage_over_time("K")
    suggest_energy_saving()

    # Benchmark comparison
    compare_with_benchmark("Kettle", total_energy_kwh)

    
def handle_washing_machine_scenario():
    print("Washing Machine Usage Scenario")
    
    # Get user input for washing details
    try:
        number_of_washes = int(input("Enter the number of washes per week: "))
        if number_of_washes <= 0:
            raise ValueError("The number of washes must be a positive integer.")
    except ValueError as e:
        print(e)
        return

    try:
        washing_temp = input("Select washing temperature (cold/warm/hot): ").strip().lower()
        if washing_temp not in ["cold", "warm", "hot"]:
            raise ValueError("Invalid temperature selection.")
    except ValueError as e:
        print(e)
        return

    try:
        cycle_type = input("Select cycle type (eco/quick/heavy): ").strip().lower()
        if cycle_type not in ["eco", "quick", "heavy"]:
            raise ValueError("Invalid cycle type selection.")
    except ValueError as e:
        print(e)
        return

    # Set default values based on user inputs
    power_rating_watts = appliance_power_ratings["Washing Machine"]  # Default power rating

    # Heating energy calculation based on temperature selection
    if washing_temp == "cold":
        heating_energy_kwh = 0  # No heating required
    elif washing_temp == "warm":
        heating_energy_kwh = calculate_energy_for_heating_water(5, ROOM_TEMPERATURE, 40, 1)  # Estimate energy for 5L water to 40°C
    else:  # hot
        heating_energy_kwh = calculate_energy_for_heating_water(5, ROOM_TEMPERATURE, 60, 1)  # Estimate energy for 5L water to 60°C

    # Cycle type adjustment
    if cycle_type == "eco":
        cycle_multiplier = 0.8  # Eco uses less energy
    elif cycle_type == "quick":
        cycle_multiplier = 1.2  # Quick wash might use more energy due to faster operations
    else:  # heavy
        cycle_multiplier = 1.5  # Heavy wash uses more energy

    # Calculate energy usage per wash
    energy_per_wash_kwh = (power_rating_watts * cycle_multiplier / 1000) + heating_energy_kwh
    weekly_energy_kwh = energy_per_wash_kwh * number_of_washes
    weekly_carbon_footprint = calculate_carbon_footprint(weekly_energy_kwh, CO2_EMISSION_FACTOR_UK)
    cost = calculate_energy_cost(weekly_energy_kwh, ELECTRICITY_RATE_PER_KWH)

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate changes
    change_yesterday, change_last_month, change_last_year = calculate_changes("Washing Machine", now, weekly_carbon_footprint)

    # Save the data to the CSV
    save_daily_data(date_str, "Washing Machine", "W", weekly_energy_kwh, weekly_carbon_footprint, change_yesterday, change_last_month, change_last_year, cost)

    # Display results
    print(f"\nEnergy Consumption for {number_of_washes} wash(es) per week (kWh): {weekly_energy_kwh:.2f}")
    print(f"Carbon Footprint for {number_of_washes} wash(es) per week (kg CO2): {weekly_carbon_footprint:.2f}")
    print(f"Change from Yesterday (kg CO2): {round(change_yesterday, 2) if change_yesterday is not None else 'N/A'}")
    print(f"Change from Last Month (kg CO2): {round(change_last_month, 2) if change_last_month is not None else 'N/A'}")
    print(f"Change from Last Year (kg CO2): {round(change_last_year, 2) if change_last_year is not None else 'N/A'}")
    print(f"Cost for Washing Machine Usage (GBP): £{round(cost, 2)}")

    cumulative_impact(weekly_energy_kwh, weekly_carbon_footprint)
    suggest_energy_saving_washing_machine(washing_temp, cycle_type)

    # Benchmark comparison
    compare_with_benchmark("Washing Machine", weekly_energy_kwh)
      # Automatically generate and display the usage visualization
    visualize_energy_and_carbon("W")  # For Kettle's energy and carbon footprint
    visualize_cost_over_time("W")  # For Kettle's cost

def calculate_energy_for_heating_water(volume_liters, initial_temp_c, final_temp_c, efficiency):
    # Specific heat capacity of water
    specific_heat_capacity = 4.18  # J/g°C
    mass_of_water = volume_liters * 1000  # Convert liters to grams
    energy_joules = mass_of_water * specific_heat_capacity * (final_temp_c - initial_temp_c)
    energy_kwh = energy_joules / (3600 * 1000)  # Convert Joules to kWh
    return energy_kwh / efficiency


def calculate_energy_consumption(power_rating_watts, usage_time_minutes, uses_per_day):
    usage_time_hours = usage_time_minutes / 60  # Convert minutes to hours
    energy_per_use_kwh = (power_rating_watts * usage_time_hours) / 1000  # Convert watts to kWh
    daily_energy_consumption_kwh = energy_per_use_kwh * uses_per_day
    return daily_energy_consumption_kwh

def compare_with_benchmark(appliance, daily_energy):
    benchmark_energy_kwh = benchmark_data[appliance]
    benchmark_daily_energy = benchmark_energy_kwh * 6  # Assuming 60 minutes of usage for comparison
    
    print(f"\nBenchmark Comparison for {appliance.title()}:")
    if daily_energy > benchmark_daily_energy:
        print(f"Your daily energy consumption ({round(daily_energy, 2)} kWh) is above the benchmark ({round(benchmark_daily_energy, 2)} kWh).")
    else:
        print(f"Your daily energy consumption ({round(daily_energy, 2)} kWh) is below the benchmark ({round(benchmark_daily_energy, 2)} kWh).")

def calculate_changes(appliance, current_date, daily_carbon_footprint):
    previous_data = read_previous_data()

    # Initialize changes to None
    change_yesterday = change_last_month = change_last_year = None

    if not previous_data:
        return change_yesterday, change_last_month, change_last_year

    yesterday_date = (current_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    last_month_date = (current_date - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    last_year_date = (current_date - datetime.timedelta(days=365)).strftime("%Y-%m-%d")

    # Get data for comparison dates
    for row in previous_data:
        row_date = row["Date"].split(" ")[0]
        if row_date == yesterday_date and row["Appliance_Type"] == appliance_abbreviations[appliance]:
            change_yesterday = daily_carbon_footprint - float(row["Daily Carbon Footprint (kg CO2)"])
        if row_date == last_month_date and row["Appliance_Type"] == appliance_abbreviations[appliance]:
            change_last_month = daily_carbon_footprint - float(row["Daily Carbon Footprint (kg CO2)"])
        if row_date == last_year_date and row["Appliance_Type"] == appliance_abbreviations[appliance]:
            change_last_year = daily_carbon_footprint - float(row["Daily Carbon Footprint (kg CO2)"])

    return change_yesterday, change_last_month, change_last_year

DATABASE_FILE = "CARBON_FOOTPRINT.db"
def read_previous_data(appliance_type=None):
    query = "SELECT * FROM appliance_data"
    params = []
    
    if appliance_type:
        query += " WHERE appliance = ?"
        params.append(appliance_type)
    
    query += " ORDER BY date ASC"
    
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def cumulative_impact(total_energy_kwh, total_carbon_footprint):
    try:
        usage_period = input("Calculate cumulative impact over how many days? (e.g., 7, 30): ")
        days = int(usage_period)
        if days <= 0:
            raise ValueError
    except ValueError:
        print("Invalid input. Skipping cumulative impact calculation.")
        return

    total_energy_cumulative = total_energy_kwh * days
    total_carbon_cumulative = total_carbon_footprint * days

    print(f"\nCumulative Energy Consumption over {days} days (kWh): {round(total_energy_cumulative, 2)}")
    print(f"\nCumulative Carbon Footprint over {days} days (kg CO2): {round(total_carbon_cumulative, 2)}")

def suggest_energy_saving():
    print("\nEnergy-Saving Tips:")
    print("- Consider boiling only the amount of water you need.")
    print("- Use a Kettle with a higher efficiency rating.")
    print("- If you frequently make tea, consider using a thermos to keep water hot longer, reducing the need to reboil.")

def suggest_energy_saving_washing_machine(washing_temp, cycle_type):
    print("\nEnergy-Saving Tips for Washing Machine:")
    if washing_temp != "cold":
        print("- Consider switching to cold washes to save energy used for heating water.")
    if cycle_type != "eco":
        print("- Use the eco-wash cycle whenever possible to reduce energy consumption.")
    print("- Wash full loads whenever possible to maximize energy efficiency.")
    print("- Consider upgrading to a more energy-efficient Washing Machine if yours is older.")


# Example usage:
#visualize_energy_and_carbon("K")  # For Kettle's energy and carbon footprint
#visualize_cost_over_time("K")  # For Kettle's cost

if __name__ == "__main__":
    main()
