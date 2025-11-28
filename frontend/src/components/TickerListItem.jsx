import { memo } from 'react';

export const TickerListItem = memo(({ tickerData, onSelect, isSelected }) => {
  if (!tickerData) return null;

  const { symbol, bids, asks, bid_qty, ask_qty } = tickerData;
  
  // Get best bid/ask
  const bestBid = bids?.[0] || 0;
  const bestAsk = asks?.[0] || 0;
  const spread = bestAsk - bestBid;
  
  // Format symbol (remove exchange prefix)
  const displaySymbol = symbol?.split(':')[1] || symbol;
  
  // Determine type
  const isFutures = symbol?.includes('FUT');
  const isCE = symbol?.includes('CE');
  const isPE = symbol?.includes('PE');

  return (
    <div 
      className={`ticker-list-item ${isSelected ? 'selected' : ''}`}
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
      <div className="ticker-list-symbol">
        {displaySymbol}
      </div>
      <div className="ticker-list-price">
        <span className="price bid">{bestBid.toFixed(2)}</span>
        <span className="spread-mini">{spread.toFixed(2)}</span>
        <span className="price ask">{bestAsk.toFixed(2)}</span>
      </div>
    </div>
  );
});

TickerListItem.displayName = 'TickerListItem';

