import React from "react";
import sunny from "./image/sunny.png";
import rain from "./image/rainy.png";
import cloud from "./image/clouds.png";
import mist from "./image/mist.png";
import cold from "./image/cold.png";
import defaultImg from "./image/weather.png";
import "./WeatherCard.css";

const WeatherCard = () => {
  const [weather, setWeather] = React.useState(null);

  React.useEffect(() => {
    fetch("http://localhost:5001/weather")
      .then(res => res.json())
      .then(data => setWeather(data));
  }, []);

  const getWeatherImage = (description) => {
    const desc = description.toLowerCase();

    if (desc.includes("rainy")) return rain;
    if (desc.includes("clouds")) return cloud;
    if (desc.includes("mist") || desc.includes("fog")) return mist;
    if (desc.includes("snow") || desc.includes("cold")) return cold;
    if (desc.includes("sun") || desc.includes("clear")) return sunny;

    return defaultImg;
  };

  if (!weather) {
    return <div className="weather-card loading">Loading...</div>;
  }

  return (
    <div className="weather-card">
      <img
        src={getWeatherImage(weather.description)}
        alt="Weather"
        className="weather-img"
      />

      <h3 className="title">🌦 Weather Today</h3>
      <p className="city">{weather.city}</p>
      <p className="temp">{weather.temperature}°C</p>
      <p className="desc">{weather.description}</p>
    </div>
  );
};

export default WeatherCard;