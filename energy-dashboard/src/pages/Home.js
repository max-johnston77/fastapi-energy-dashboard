import React, { useState } from "react";
import Dashboard from "../components/Dashboard";

const Home = () => {
  const [selectedHub, setSelectedHub] = useState("Chryston");

  return (
    <div>
      <h1>Energy Dashboard</h1>
      <label>Select Hub:</label>
      <select value={selectedHub} onChange={(e) => setSelectedHub(e.target.value)}>
        <option value="Chryston">Chryston</option>
        <option value="Sunnyside">Sunnyside</option>
        <option value="Cumbernauld Village">Cumbernauld Village</option>
        <option value="Denmilne Summerhouse">Denmilne Summerhouse</option>
        <option value="Clyde Cycle Park">Clyde Cycle Park</option>
      </select>
      <Dashboard hubName={selectedHub} />
    </div>
  );
};

export default Home;

