import React, { useEffect, useState } from "react";

const MarketPricesCard = () => {
    const [prices, setPrices] = useState("Loading...");

    const fetchPrices = async () => {
        try {
            const res = await fetch("http://localhost:5001/market-prices");
            const data = await res.json();
            setPrices(data.prices || "No data");
        } catch (err) {
            setPrices("Failed to load market prices");
        }
    };

    useEffect(() => {
        fetchPrices();

        // auto refresh every 6 hours (optional "daily feel")
        const interval = setInterval(fetchPrices, 21600000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="market-price-card">
            <h3>📊 Daily Market Prices</h3>
            <pre style={{ whiteSpace: "pre-wrap" }}>{prices}</pre>
        </div>
    );
};

export default MarketPricesCard;