import { memo } from 'react';

export const TickerCard = memo(({ tickerData, onSelect, isSelected }) => {
  if (!tickerData) return null;

  const { symbol, tbq, tsq, bids, asks, bid_qty, ask_qty, server_latencies } = tickerData;
  
  // Get best bid/ask (first in array)
  const bestBid = bids?.[0] || 0;
  const bestAsk = asks?.[0] || 0;
  const bestBidQty = bid_qty?.[0] || 0;
  const bestAskQty = ask_qty?.[0] || 0;
  const spread = bestAsk - bestBid;
  
  // Format symbol (remove exchange prefix)
  const displaySymbol = symbol?.split(':')[1] || symbol;

  return (
    <div 
      className={`ticker-card ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect?.();
        }
      }}
    >
      <div className="ticker-header">
        <h3 className="ticker-symbol">{displaySymbol}</h3>
        {server_latencies?.end_to_end_s && (
          <span className="latency">
            {((server_latencies.end_to_end_s || 0) * 1000).toFixed(2)}ms
          </span>
        )}
      </div>
      
      <div className="ticker-stats">
        <div className="stat-item">
          <span className="stat-label">Total Buy Qty</span>
          <span className="stat-value buy">{tbq?.toLocaleString() || 0}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Total Sell Qty</span>
          <span className="stat-value sell">{tsq?.toLocaleString() || 0}</span>
        </div>
      </div>

      <div className="orderbook-preview">
        <div className="bid-side">
          <div className="orderbook-header">Bids</div>
          <div className="orderbook-row">
            <span className="price bid">{bestBid.toFixed(2)}</span>
            <span className="qty">{bestBidQty.toLocaleString()}</span>
          </div>
        </div>
        <div className="spread-info">
          <span className="spread-label">Spread</span>
          <span className="spread-value">{spread.toFixed(2)}</span>
        </div>
        <div className="ask-side">
          <div className="orderbook-header">Asks</div>
          <div className="orderbook-row">
            <span className="price ask">{bestAsk.toFixed(2)}</span>
            <span className="qty">{bestAskQty.toLocaleString()}</span>
          </div>
        </div>
      </div>
      
      {onSelect && (
        <div className="ticker-hint">Click to view order book</div>
      )}
    </div>
  );
});

TickerCard.displayName = 'TickerCard';