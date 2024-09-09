# calculations.py
from modules.utils import benchmark_data
from modules.database import read_previous_data 
from modules.utils import datetime, appliance_abbreviations


CO2_EMISSION_FACTOR_UK = 0.233  # kg CO2 per kWh (as of 2023)
ELECTRICITY_RATE_PER_KWH = 0.28  # £0.28 per kWh

def calculate_energy_consumption(power_rating_watts, usage_time_minutes, uses_per_day):
    usage_time_hours = usage_time_minutes / 60  # Convert minutes to hours
    energy_per_use_kwh = (power_rating_watts * usage_time_hours) / 1000  # Convert watts to kWh
    daily_energy_consumption_kwh = energy_per_use_kwh * uses_per_day
    return round(daily_energy_consumption_kwh,4)

def calculate_carbon_footprint(energy_consumption_kwh):
    return round(energy_consumption_kwh * CO2_EMISSION_FACTOR_UK,4)

def calculate_energy_cost(energy_kwh):
    return round(energy_kwh * ELECTRICITY_RATE_PER_KWH,4)


def calculate_energy_for_heating_water(volume_liters, initial_temp_c, final_temp_c, efficiency):
    # Specific heat capacity of water
    specific_heat_capacity = 4.18  # J/g°C
    mass_of_water = volume_liters * 1000  # Convert liters to grams
    energy_joules = mass_of_water * specific_heat_capacity * (final_temp_c - initial_temp_c)
    energy_kwh = energy_joules / (3600 * 1000)  # Convert Joules to kWh
    return round(energy_kwh / efficiency,4)


def calculate_energy_consumption(power_rating_watts, usage_time_minutes, uses_per_day):
    usage_time_hours = usage_time_minutes / 60  # Convert minutes to hours
    energy_per_use_kwh = (power_rating_watts * usage_time_hours) / 1000  # Convert watts to kWh
    daily_energy_consumption_kwh = energy_per_use_kwh * uses_per_day
    return round(daily_energy_consumption_kwh,4) 

def compare_with_benchmark(appliance, daily_energy):
    benchmark_energy_kwh = benchmark_data[appliance]
    benchmark_daily_energy = benchmark_energy_kwh * 6  # Assuming 60 minutes of usage for comparison
    
    print(f"\nBenchmark Comparison for {appliance.title()}:")
    if daily_energy > benchmark_daily_energy:
        print(f"Your daily energy consumption ({round(daily_energy, 4)} kWh) is above the benchmark ({round(benchmark_daily_energy, 4)} kWh).")
    else:
        print(f"Your daily energy consumption ({round(daily_energy, 4)} kWh) is below the benchmark ({round(benchmark_daily_energy, 4)} kWh).")

def calculate_changes(appliance, current_date, daily_carbon_footprint):
    previous_data = read_previous_data(appliance)

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

        try:
            # Check if the value is convertible to float
            previous_footprint = float(row["Daily Carbon Footprint (kg CO2)"])
        except (ValueError, KeyError, TypeError) as e:
            print(f"Error converting value: {e}. Row: {row}")
            continue

        if row_date == yesterday_date and row["Appliance_Type"] == appliance_abbreviations[appliance]:
            change_yesterday = daily_carbon_footprint - previous_footprint
        if row_date == last_month_date and row["Appliance_Type"] == appliance_abbreviations[appliance]:
            change_last_month = daily_carbon_footprint - previous_footprint
        if row_date == last_year_date and row["Appliance_Type"] == appliance_abbreviations[appliance]:
            change_last_year = daily_carbon_footprint - previous_footprint

    return change_yesterday, change_last_month, change_last_year


def calculate_energy_cost(energy_kwh, rate_per_kwh):
    return energy_kwh * rate_per_kwh

# Example values
energy_per_wash_kwh = 1.2  # Energy used per wash in kWh
ELECTRICITY_RATE_PER_KWH = 0.28  # Cost per kWh in your currency, e.g., £0.28


