from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file
from modules.users import register_user, check_password_hash, generate_password_hash, login_user
from modules.appliances import handle_appliance_scenario, calculate_changes, DEFAULT_CUP_VOLUME_ML, DEFAULT_Kettle_EFFICIENCY,WATER_DENSITY,handle_appliance_scenario, check_maintenance_reminder,appliance_power_ratings, visualize_cost_over_time,calculate_carbon_footprint,calculate_changes, calculate_energy_consumption, calculate_energy_cost
from modules.visualisation import visualize_energy_and_carbon, visualize_cost_over_time
from modules.utils import  maintenance_intervals, usage_scenarios, appliance_abbreviations,appliance_power_ratings, benchmark_data, datetime, register_user, login_user
from modules.calculations import CO2_EMISSION_FACTOR_UK,ELECTRICITY_RATE_PER_KWH, calculate_energy_cost
from modules.database import ensure_db, save_daily_data, update_maintenance_date,sqlite3
from modules.appliances import calculate_energy_consumption,calculate_changes, DEFAULT_CUP_VOLUME_ML, calculate_energy_for_cup_of_tea,calculate_energy_for_heating_water, ROOM_TEMPERATURE,BOILING_POINT, DEFAULT_Kettle_EFFICIENCY

import sqlite3
import hashlib
#import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template
import io
import base64
from dateutil import parser 
from modules.visualisation import visualize_energy_and_carbon, visualize_cost_over_time, fetch_cost_data, fetch_energy_and_carbon_data, DATABASE_FILE




app = Flask(__name__)
def home():
    return render_template('index.html') 

app.secret_key = 'your_secret_key'
#DATABASE = 'database/CARBON_FOOTPRINT.db'
DATABASE = r"C:\Users\User\Documents\FinalMSCProject\database\CARBON_FOOTPRINT.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    password = hash_password(password)
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()
    return user

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = verify_user(username, password)
        if user:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hash_password(password)))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Add routes for calculating energy usage, maintenance reminders, and visualizations
# ...
@app.route('/select-appliance', methods=['GET', 'POST'])
def select_appliance():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        appliance = request.form['appliance']
        if appliance == "Kettle":
            return redirect(url_for('handle_kettle'))
        elif appliance == "Washing Machine":
            return redirect(url_for('handle_washing_machine'))
        else:
            return redirect(url_for('handle_general_appliance', appliance=appliance))
    
    return render_template('select_appliance.html')



@app.route('/handle-kettle', methods=['GET', 'POST'])
def handle_kettle():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # User inputs
            number_of_cups = int(request.form['number_of_cups'])
            custom_cup_size = request.form.get('cup_size', DEFAULT_CUP_VOLUME_ML)
            cup_size_ml = float(custom_cup_size) if custom_cup_size else DEFAULT_CUP_VOLUME_ML
            starting_temp = int(request.form.get('starting_temp', ROOM_TEMPERATURE))

            # Calculate energy consumption for the current usage
            total_energy_kwh = round(calculate_energy_for_cup_of_tea(cup_size_ml, starting_temp, BOILING_POINT, DEFAULT_Kettle_EFFICIENCY) * number_of_cups, 2)
            total_carbon_footprint = round(calculate_carbon_footprint(total_energy_kwh), 4)
            cost = round(calculate_energy_cost(total_energy_kwh, ELECTRICITY_RATE_PER_KWH), 4)

            # Get the current date and time
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d %H:%M:%S")

            # Comparison with previous data (yesterday, last month, last year)
            change_yesterday, change_last_month, change_last_year = calculate_changes("Kettle", now, total_carbon_footprint)

            # Benchmark Comparison
            benchmark_energy_kwh = 0.19  # 0.19 kWh benchmark for boiling 1.7 liters of water
            benchmark_cost = 0.07  # 7p benchmark cost for boiling 1.7 liters of water
            tips = []

            if total_energy_kwh > benchmark_energy_kwh:
                tips = [
                    "Don't overfill your kettle. Only boil the amount of water you need to save energy.",
                    "Consider switching to an energy-efficient model that boils water faster and uses less energy.",
                    "Descale your kettle regularly to prevent limescale build-up, which can reduce energy efficiency."
                ]
            else:
                tips = ["Great job! Your kettle usage is efficient and below the benchmark. Keep up the good energy habits!"]

            # Save the data to the database
            save_daily_data(date_str, "Kettle", "K", total_energy_kwh, total_carbon_footprint, change_yesterday, change_last_month, change_last_year, cost)

            # Render the results page with the calculated data, comparisons, and tips
            return render_template('kettle_result.html', 
                                   total_energy_kwh=total_energy_kwh, 
                                   total_carbon_footprint=total_carbon_footprint, 
                                   cost=cost,
                                   change_yesterday=change_yesterday,
                                   change_last_month=change_last_month,
                                   change_last_year=change_last_year,
                                   benchmark_energy_kwh=benchmark_energy_kwh,
                                   benchmark_cost=benchmark_cost,
                                   tips=tips)

        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('handle_kettle.html')

    return render_template('handle_kettle.html')



@app.route('/handle-washing-machine', methods=['GET', 'POST'])
def handle_washing_machine():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Get user input
            number_of_washes = int(request.form['number_of_washes'])
            washing_temp = request.form['washing_temp'].strip().lower()
            cycle_type = request.form['cycle_type'].strip().lower()
            
            # Validate input
            if number_of_washes <= 0:
                raise ValueError("The number of washes must be a positive integer.")
            if washing_temp not in ["cold", "warm", "hot"]:
                raise ValueError("Invalid washing temperature selection.")
            if cycle_type not in ["eco", "quick", "heavy"]:
                raise ValueError("Invalid cycle type selection.")
            
            # Power rating for Washing Machine
            power_rating_watts = appliance_power_ratings["Washing Machine"]

            # Heating energy calculation based on temperature selection
            if washing_temp == "cold":
                heating_energy_kwh = 0  # No heating required
            elif washing_temp == "warm":
                heating_energy_kwh = calculate_energy_for_heating_water(5, ROOM_TEMPERATURE, 40, 1)
            else:  # hot
                heating_energy_kwh = calculate_energy_for_heating_water(5, ROOM_TEMPERATURE, 60, 1)

            # Cycle type adjustment
            if cycle_type == "eco":
                cycle_multiplier = 0.8  # Eco uses less energy
            elif cycle_type == "quick":
                cycle_multiplier = 1.2  # Quick wash might use more energy due to faster operations
            else:  # heavy
                cycle_multiplier = 1.5  # Heavy wash uses more energy

            # Calculate energy usage per wash
            energy_per_wash_kwh = round((power_rating_watts * cycle_multiplier / 1000) + heating_energy_kwh, 2)
            
        
            # Calculate carbon footprint per wash
            #carbon_footprint_per_wash = round(calculate_carbon_footprint(energy_per_wash_kwh, CO2_EMISSION_FACTOR_UK), 4)
            carbon_footprint_per_wash = round(calculate_carbon_footprint(energy_per_wash_kwh), 4)

            
            # Calculate cost per wash
            cost_per_wash = round(calculate_energy_cost(energy_per_wash_kwh, ELECTRICITY_RATE_PER_KWH), 4)
            
            print(f"Cost per wash: {cost_per_wash} currency units")
    
            # Calculate totals for the week
            weekly_energy_kwh = round(energy_per_wash_kwh * number_of_washes, 4)
            weekly_carbon_footprint = round(carbon_footprint_per_wash * number_of_washes, 4)
            weekly_cost = round(cost_per_wash * number_of_washes, 4)

            # Benchmark data
            benchmark_kwh_per_wash = 1.2  # D-rated machine benchmark value in kWh
            tips = []

            # Compare with benchmark and provide tips if necessary
            if energy_per_wash_kwh > benchmark_kwh_per_wash:
                message = f"Benchmark for a D+ washing machine is {benchmark_kwh_per_wash} kWh, and your current energy usage is {energy_per_wash_kwh:.2f} kWh. Therefore, your usage is above the UK benchmark."
                tips = [
                    "Consider washing full loads to maximize energy efficiency.",
                    "Using cold water can significantly reduce energy usage, as heating water consumes most of the energy.",
                    "Opt for shorter wash cycles when possible to save on energy and costs.",
                    "Maintain your washing machine regularly by cleaning the lint filter and checking for clogs.",
                    "When it's time to replace your washing machine, consider an energy-efficient model with an Energy Star rating."
                ]
            else:
                message = f"Benchmark for a D+ washing machine is {benchmark_kwh_per_wash} kWh, and your current energy usage is {energy_per_wash_kwh:.2f} kWh. Great job on being energy-efficient, as your usage is below the benchmark!"
                tips = ["Your washing machine's energy usage is below the benchmark, great job on being energy-efficient!"]
            # Display the message and tips
            print(message)
            for tip in tips:
             print(f"- {tip}")


            # Get the current date and time
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d %H:%M:%S")

            # Save the data to the database
            save_daily_data(date_str, "Washing Machine", "W", weekly_energy_kwh, weekly_carbon_footprint, None, None, None, weekly_cost)

            # Render the results page with the calculated data and tips
            return render_template('washing_machine_result.html', 
                                   energy_per_wash_kwh=energy_per_wash_kwh, 
                                   carbon_footprint_per_wash=carbon_footprint_per_wash,
                                   cost_per_wash=cost_per_wash,
                                   weekly_energy_kwh=weekly_energy_kwh, 
                                   weekly_carbon_footprint=weekly_carbon_footprint, 
                                   weekly_cost=weekly_cost,
                                   tips=tips)

        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('handle_washing_machine.html')

    return render_template('handle_washing_machine.html')



@app.route('/handle-general-appliance/<appliance>', methods=['GET', 'POST'])
def handle_general_appliance(appliance):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # handle general appliance scenario logic here
        return render_template('general_appliance_result.html', result=result)

    return render_template('handle_general_appliance.html', appliance=appliance)


@app.route('/maintenance-reminder')
def maintenance_reminder():
    # Logic for maintenance reminders
    return render_template('maintenance_reminder.html')


@app.route('/visualize/energy-usage', methods=['GET'])
def visualize_energy_usage():
    return render_template('visualize_energy_usage.html')



@app.route('/visualize/energy/<appliance_letter>')
def visualize_energy_and_carbon(appliance_letter):
    data = fetch_energy_and_carbon_data(appliance_letter)
    
    if not data:
        return "No data available for the selected appliance.", 404

    dates, energies, carbon_footprints = zip(*[
        (parser.parse(row[0]), float(row[1]), float(row[2])) 
        for row in data if row[1] is not None and row[2] is not None
    ])
    
    # Create the figure using Matplotlib
    plt.figure(figsize=(10, 8))
    plt.plot(dates, energies, marker='o', label='Energy Usage (kWh)', color='blue')
    plt.plot(dates, carbon_footprints, marker='o', label='Carbon Footprint (kg CO2)', color='green')
    plt.title(f'{appliance_letter} Energy Usage and Carbon Footprint Over Time')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # Save the figure to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)  # Move to the beginning of the BytesIO object
    plt.close()  # Close the plot

    # Send the image as a response with the correct mimetype
    return send_file(img, mimetype='image/png')
    #image_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    # Render the HTML page with the image
    #return render_template('visualization.html', image_data=image_base64)

@app.route('/visualize/cost/<appliance_letter>')
def visualize_cost_route(appliance_letter):
    img = io.BytesIO()
    visualize_cost_over_time(appliance_letter)  # This function generates the graph
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    #return send_file(img, mimetype='image/png')
    image_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return render_template('visualize_cost.html', image_data=image_base64)


@app.route('/visualize')
def visualize_home():
    return render_template('visualize_home.html')


if __name__ == '__main__':
    app.run(debug=True)
