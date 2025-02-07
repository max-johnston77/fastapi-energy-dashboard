import requests
import pandas as pd
import json
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# Initialize FastAPI app
app = FastAPI()


# Enable CORS for React frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Renewables Ninja API settings
TOKEN = 'b3b0b74b1cf6795f36bb9246b9ac3c9b6098b2eb'
API_BASE = 'https://www.renewables.ninja/api/'

# Define multiple locations
locations = [
    {"name": "Chryston", "lat": 55.9054, "lon": -4.1011, "capacity": 4, "system_loss": 0, "tracking": 0, "tilt": 30, "azim": 180},
    {"name": "Sunnyside", "lat": 55.8570, "lon": -4.2378, "capacity": 4, "system_loss": 0, "tracking": 0, "tilt": 0, "azim": 190},
    {"name": "Cumbernauld Village", "lat": 55.9629, "lon": -3.9766, "capacity": 4, "system_loss": 0, "tracking": 0, "tilt": 30, "azim": 170},
    {"name": "Denmilne Summerhouse", "lat": 55.8634, "lon": -4.1031, "capacity": 4, "system_loss": 0, "tracking": 0, "tilt": 30, "azim": 200},
    {"name": "Clyde Cycle Park", "lat": 55.8310, "lon": -4.1836, "capacity": 4, "system_loss": 0, "tracking": 0, "tilt": 15, "azim": 180},
]

# API session
s = requests.session()
s.headers = {'Authorization': 'Token ' + TOKEN}


@app.get("/solar-data/{location_name}")
def get_solar_data(location_name: str):
    # Find the location data
    location = next((loc for loc in locations if loc["name"].lower() == location_name.lower()), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

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
        response = s.get(API_BASE + 'data/pv', params=args)
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

            # Prepare data to return
            output_data = {
                "location": location["name"],
                "time_series": [
                    {
                        "time": str(time_range[i]),
                        "battery_charge": (battery_charge[i] / battery_capacity) * 100,  # Convert to percentage
                        "demand_kwh": demand[i],
                        "solar_generation_kwh": hourly_generation.iloc[i],
                    }
                    for i in range(len(time_range))
                ],
                "total_generation_kwh": hourly_generation.sum(),
                "bikes_equivalent": int(hourly_generation.sum() / 0.5),  # Assuming each e-bike charge = 0.5 kWh
            }

            return output_data

        else:
            raise HTTPException(status_code=response.status_code, detail="Error fetching solar data")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/")
def home():
    return {"message": "Welcome to the Solar Energy API. Use /solar-data/{location_name} to get data."}

