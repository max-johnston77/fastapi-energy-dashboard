import React, { useState, useEffect } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ResponsiveContainer } from "recharts";

const Dashboard = ({ hubName }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
      axios.get(`http://127.0.0.1:8000/solar-data/${hubName}`)
      .then((response) => {
        const formattedData = response.data.time_series.map((entry) => ({
          time: entry.time,
          batteryCharge: entry.battery_charge,
          demand: entry.demand_kwh,
          solarGeneration: entry.solar_generation_kwh,
        }));
        setData(formattedData);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, [hubName]);

  return (
    <div>
      <h2>Energy Profile for {hubName}</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 10 }}>
          <XAxis dataKey="time" tickFormatter={(tick) => tick.split(" ")[1]} />
          <YAxis yAxisId="left" label={{ value: "kWh", angle: -90, position: "insideLeft" }} />
          <YAxis yAxisId="right" orientation="right" label={{ value: "Battery (%)", angle: 90, position: "insideRight" }} />
          <Tooltip />
          <Legend />
          <CartesianGrid strokeDasharray="3 3" />
          <Line yAxisId="left" type="monotone" dataKey="demand" stroke="red" name="Demand (kWh)" />
          <Line yAxisId="left" type="monotone" dataKey="solarGeneration" stroke="green" name="Solar Generation (kWh)" />
          <Line yAxisId="right" type="monotone" dataKey="batteryCharge" stroke="blue" name="Battery Charge (%)" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default Dashboard;

