import React, { useEffect, useState } from "react";
import "./ChatLayout.css";

export default function MarketPricesCard() {
    const [marketData, setMarketData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch("http://localhost:5001/market?location=Erode&language=English")
            .then((res) => res.json())
            .then((data) => {
                console.log("MARKET FRONTEND DATA:", data);
                setMarketData(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Market fetch error:", err);
                setLoading(false);
            });
    }, []);

    return (
        <div className="market-card">
            <h3 className="market-title">📈 Latest Market Update</h3>

            {loading && <div className="market-loading">Loading...</div>}

            {!loading && !marketData && (
                <div className="market-loading">No data available</div>
            )}

            {!loading && marketData && (
                <div style={{
                    whiteSpace: "pre-wrap",
                    lineHeight: "1.6",
                    background: "#f8f7f7",
                    color: "#000000",
                    padding: "12px",
                    borderRadius: "10px",
                    marginTop: "8px"
                }}>
                    <p><strong>Location:</strong> {marketData.location || "Unknown"}</p>
                    <p><strong>Language:</strong> {marketData.language || "English"}</p>
                    <p><strong>Summary:</strong></p>
                    <div
                        style={{
                            whiteSpace: "pre-wrap",
                            lineHeight: "1.5",
                            background: "rgba(255,255,255,0.08)",
                            padding: "10px",
                            borderRadius: "10px",
                            marginTop: "8px"
                        }}
                    >
                        {marketData.summary || "No summary available"}
                    </div>
                </div>
            )}
        </div>
    );
}