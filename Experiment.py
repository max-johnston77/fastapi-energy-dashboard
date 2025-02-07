import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
import time  # For introducing delays

# Renewables Ninja API settings
token = 'b3b0b74b1cf6795f36bb9246b9ac3c9b6098b2eb'
api_base = 'https://www.renewables.ninja/api/'

# Define multiple locations with their parameters
locations = [
    {"name": "Chryston", "lat": 55.9054, "lon": -4.1011, "capacity": 4, "system_loss": 0, "tracking": 0, "tilt": 30, "azim": 180},
    {"name": "Sunnyside", "lat": 55.8570, "lon": -4.2378, "capacity": 4, "system_loss": 0, "tracking": 0, "tilt": 0, "azim": 190},
    {"name": "Cumbernauld Village", "lat": 55.9629, "lon": -3.9766, "capacity": 4, "system_loss": 0, "tracking": 0, "tilt": 30, "azim": 170},
    {"name": "Denmilne Summerhouse", "lat": 55.8634, "lon": -4.1031, "capacity": 4, "system_loss": 0, "tracking": 0, "tilt": 30, "azim": 200},
    {"name": "Clyde Cycle Park", "lat": 55.8310, "lon": -4.1836, "capacity": 4, "system_loss": 0, "tracking": 0, "tilt": 15, "azim": 180},
]

# API session
s = requests.session()
s.headers = {'Authorization': 'Token ' + token}

# Processing each location
for location in locations:
    print(f"Processing {location['name']}...")

    args = {
        'lat': location['lat'],
        'lon': location['lon'],
        'date_from': '2023-12-09',
        'date_to': '2023-12-10',
        'dataset': 'merra2',
        'capacity': location['capacity'],
        'system_loss': location['system_loss'],
        'tracking': location['tracking'],
        'tilt': location['tilt'],
        'azim': location['azim'],
        'format': 'json',
    }

    # API request with delay
    try:
        response = s.get(api_base + 'data/pv', params=args)
        time.sleep(2)  # Add a delay to prevent burst limit issues

        if response.status_code == 200:
            # Parse API response
            data = pd.read_json(json.dumps(response.json()['data']), orient='index')
            data.index = pd.to_datetime(data.index)

            # Create hourly time range
            time_range = pd.date_range(start="2023-12-09", end="2023-12-10", freq="H")[:-1]
            demand = [0.002 for _ in range(24)]  # Constant demand for simplicity

            # Align solar generation with time range
            hourly_generation = data['electricity'].reindex(time_range, method='nearest')

            # Battery simulation
            battery_capacity = 10  # Fixed capacity in kWh
            battery_charge = [0.02]  # Start with 2% charge

            for i in range(1, len(time_range)):
                new_charge = battery_charge[i - 1] - demand[i] + hourly_generation.iloc[i]
                new_charge = max(0, new_charge)  # No negative battery charge
                new_charge = min(battery_capacity, new_charge)  # Cap battery at its capacity
                battery_charge.append(new_charge)

            # Prepare DataFrame for plotting
            plot_data = pd.DataFrame({
                'Time': time_range,
                'Battery Charge (%)': [(charge / battery_capacity) * 100 for charge in battery_charge],  # Convert to percentage
                'Demand (kWh)': demand,
                'Solar Generation (kWh)': hourly_generation,
            }).set_index('Time')

            # Create figure and axes
            fig, ax1 = plt.subplots(figsize=(12, 6))

            # Left y-axis for demand and solar generation
            ax1.plot(plot_data.index, plot_data['Demand (kWh)'], label='Demand (kWh)', color='red', linestyle='--', marker='x')
            ax1.plot(plot_data.index, plot_data['Solar Generation (kWh)'], label='Solar Generation (kWh)', color='green', linestyle='-', marker='.')
            ax1.set_xlabel("Time")
            ax1.set_ylabel("Energy (kWh)")
            ax1.tick_params(axis='y', labelcolor='black')

            # Right y-axis for battery charge percentage
            ax2 = ax1.twinx()
            ax2.plot(plot_data.index, plot_data['Battery Charge (%)'], label='Battery Charge (%)', color='blue', marker='o')
            ax2.set_ylabel("Battery Charge (%)")
            ax2.tick_params(axis='y', labelcolor='blue')

            # Title and legend
            plt.title(f"Energy Profile for {location['name']}")
            fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
            plt.xticks(rotation=45)
            plt.grid()
            plt.tight_layout()

            # Save and display the plot
            plt.savefig(f"energy_profile_{location['name'].replace(' ', '_').lower()}.png")
            plt.show()

            # Print summary
            total_generation = hourly_generation.sum()
            print(f"Total solar generation for {location['name']}: {total_generation:.2f} kWh")
            print(f"Equivalent to charging {total_generation / 0.5:.0f} bikes.\n")

        else:
            print(f"Error fetching data for {location['name']}: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"An error occurred while processing {location['name']}: {e}")



