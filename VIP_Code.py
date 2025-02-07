import requests
import pandas as pd
import json
import datetime

# Renewables Ninja API settings
token = 'b3b0b74b1cf6795f36bb9246b9ac3c9b6098b2eb'
api_base = 'https://www.renewables.ninja/api/'

s = requests.session()
# Send token header with each request
s.headers = {'Authorization': 'Token ' + token}

# Define multiple locations with their parameters
locations = [
    {
        "name": "Chryston", 
        "lat": 55.9054, 
        "lon": -4.1011, 
        "capacity": 0.13, 
        "system_loss": 0, 
        "tracking": 0, 
        "tilt": 30, 
        "azim": 180
    },
    {
        "name": "Sunnyside", 
        "lat": 55.8570, 
        "lon": -4.2378, 
        "capacity": 0.5, 
        "system_loss": 0, 
        "tracking": 0, 
        "tilt": 0, 
        "azim": 190
    },
    {
        "name": "Cumberuald Village", 
        "lat": 55.9629, 
        "lon": -3.9766, 
        "capacity": 1.2, 
        "system_loss": 0, 
        "tracking": 0, 
        "tilt": 30, 
        "azim": 170
    },
    {
        "name": "Denmilne Summerhouse", 
        "lat": 55.8634, 
        "lon": -4.1031, 
        "capacity": 1, 
        "system_loss": 0, 
        "tracking": 0, 
        "tilt": 30, 
        "azim": 200
    },
    {
        "name": "Clyde Cycle Park", 
        "lat": 55.8310, 
        "lon": -4.1836, 
        "capacity": 3, 
        "system_loss": 0, 
        "tracking": 0, 
        "tilt": 15, 
        "azim": 180
    }
]

# Iterate over locations to fetch data and forecast
for location in locations:
    print(f"Processing {location['name']}...")

    args = {
        'lat': location['lat'],
        'lon': location['lon'],
        'date_from': '2023-01-01',
        'date_to': '2023-12-31',
        'dataset': 'merra2',
        'capacity': location['capacity'],
        'system_loss': location['system_loss'],
        'tracking': location['tracking'],
        'tilt': location['tilt'],
        'azim': location['azim'],
        'format': 'json'
    }

    # Make the request to the Renewables Ninja API
    r = s.get(api_base + 'data/pv', params=args)

    # Check if the response is valid
    if r.status_code == 200:
        try:
            # Parse JSON to get a pandas DataFrame of data and dict of metadata
            parsed_response = r.json()

            # Extract the data
            data = pd.read_json(json.dumps(parsed_response['data']), orient='index')
            metadata = parsed_response['metadata']

            # Extract the column for electricity generation ('electricity')
            # Convert the generation data to daily sums (assuming it's hourly data)
            daily_generation = data['electricity'].resample('D').sum()

            # Get the current month to make the prediction more specific to the time of year
            current_month = datetime.datetime.now().month
            current_month_data = daily_generation[daily_generation.index.month == current_month]

            # Forecast today's generation based on the average of the same month in previous years
            if len(current_month_data) > 0:
                average_monthly_generation = current_month_data.mean()
            else:
                average_monthly_generation = daily_generation.mean()  # Fallback to overall average if no data available for current month

            # Assuming you want to forecast for today and display it to users
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            forecasted_generation = average_monthly_generation

            # Convert energy into equivalent bicycles charged
            # Assuming each electric bike takes around 0.5 kWh for a full charge
            energy_per_bike_charge = 0.5
            number_of_bikes = forecasted_generation / energy_per_bike_charge

            # Output the result to the community
            print(f"The expected solar generation for {location['name']} on {today} is {forecasted_generation:.2f} kWh, this is the equivalent of {number_of_bikes:.0f} bikes.")

            # Optionally, save the data to CSV for further analysis
            daily_generation.to_csv(f"daily_solar_generation_{location['name'].replace(' ', '_').lower()}.csv")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for {location['name']}:", e)
    else:
        print(f"Error fetching data for {location['name']} from Renewables Ninja API: {r.status_code} - {r.text}")
        if r.status_code == 403:
            print("It looks like your token may be invalid or expired. Please check your token and try again.")
