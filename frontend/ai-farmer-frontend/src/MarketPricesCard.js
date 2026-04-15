import React, { useEffect, useState } from "react";
import "./MarketPricesCard.css";

const MarketPricesCard = () => {
    const [prices, setPrices] = useState([]);

    const fetchPrices = async () => {
        try {
            const res = await fetch("http://localhost:5001/market-prices");
            const data = await res.json();

            // ✅ HANDLE ERROR RESPONSE
            if (data.error) {
                console.log("API Error:", data.error);
                setPrices([]);
                return;
            }

            // ✅ HANDLE STRING RESPONSE SAFELY
            if (data.prices && typeof data.prices === "string") {
                const cleanData = data.prices
                    .split("\n")
                    .filter(line => line.includes("-")); // remove empty/bad lines

                setPrices(cleanData);
            } else {
                setPrices([]);
            }

        } catch (err) {
            console.error("Market price fetch error:", err);
            setPrices([]);
        }
    };

    useEffect(() => {
        fetchPrices();

        // 🔥 Auto refresh every 10 sec
        const interval = setInterval(fetchPrices, 10000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="market-prices-card">
            <h3 className="market-title">🌾 Live Market Prices</h3>

            {prices.length === 0 ? (
                <p className="loading-text">Loading prices...</p>
            ) : (
                <div className="price-list scroll-box">
                    {prices.map((item, index) => {
                        const parts = item.split(" - ");
                        return (
                            <div key={index} className="price-card">
                                <span className="crop">🌿 {parts[0]}</span>
                                <span className="price">₹ {parts[1]}</span>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default MarketPricesCard;