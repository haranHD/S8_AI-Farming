import "./MarketHeader.css";

const MarketHeader = () => {
  return (
    <div className="market-header">
      <div className="sell">
        🌾 Selling Prices
      </div>
      <div className="buy">
        🛒 Buying Prices
      </div>
    </div>
  );
};

export default MarketHeader;
