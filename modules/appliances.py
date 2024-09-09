from modules.calculations import calculate_energy_consumption, calculate_carbon_footprint, calculate_energy_cost ,calculate_energy_for_heating_water,calculate_changes, compare_with_benchmark
from modules.database import save_daily_data
from modules.utils import get_current_datetime , datetime, appliance_power_ratings
from modules.visualisation import visualize_energy_and_carbon , visualize_cost_over_time



CO2_EMISSION_FACTOR_UK = 0.233  # kg CO2 per kWh (as of 2023)
ELECTRICITY_RATE_PER_KWH = 0.28  # £0.28 per kWh

# Consts for the Kettle scenario
SPECIFIC_HEAT_CAPACITY_WATER = 4.18  # J/g°C
ROOM_TEMPERATURE = 20  # °C
BOILING_POINT = 100  # °C
DEFAULT_CUP_VOLUME_ML = 250  # Standard cup size in milliliters
WATER_DENSITY = 1  # g/ml (approximation)
DEFAULT_Kettle_EFFICIENCY = 0.9  # 90% efficiency


def calculate_energy_for_cup_of_tea(volume_ml, temp_start, temp_end, efficiency=DEFAULT_Kettle_EFFICIENCY):
    mass_g = volume_ml * WATER_DENSITY  # g
    energy_joules = mass_g * SPECIFIC_HEAT_CAPACITY_WATER * (temp_end - temp_start)
    energy_kwh = (energy_joules / 3.6e6) / efficiency  # Convert to kWh and adjust for efficiency
    return energy_kwh



def handle_appliance_scenario(appliance):

    # Implement your scenarios for each appliance here, similar to the original code
    pass
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
    total_carbon_footprint = calculate_carbon_footprint(total_energy_kwh, CO2_EMISSION_FACTOR_UK)
    cost = calculate_energy_cost(total_energy_kwh, ELECTRICITY_RATE_PER_KWH)

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

def check_maintenance_reminder():
    # Implement the maintenance reminder logic here
    pass

# Add more appliance-specific functions as needed...
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
