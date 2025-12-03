import { memo, useEffect, useState, useRef } from 'react';

export const TickerListItem = memo(({ tickerData, onSelect, isSelected }) => {
  if (!tickerData) return null;

  const { symbol, bids, asks, ltp } = tickerData;
  const prevPriceRef = useRef(ltp || 0);
  const [flashClass, setFlashClass] = useState('');

  // Get best bid/ask or use LTP
  const bestBid = bids?.[0] || 0;
  const bestAsk = asks?.[0] || 0;
  const currentPrice = ltp || bestBid || 0;
  const spread = (bestAsk && bestBid) ? bestAsk - bestBid : 0;

  // Format symbol (remove exchange prefix)
  const displaySymbol = symbol?.split(':')[1] || symbol;

  // Determine type
  const isFutures = symbol?.includes('FUT');
  const isCE = symbol?.includes('CE');
  const isPE = symbol?.includes('PE');
  const isIndexOrStock = !isFutures && !isCE && !isPE;

  useEffect(() => {
    if (currentPrice > prevPriceRef.current) {
      setFlashClass('flash-up');
    } else if (currentPrice < prevPriceRef.current) {
      setFlashClass('flash-down');
    }

    prevPriceRef.current = currentPrice;

    const timer = setTimeout(() => {
      setFlashClass('');
    }, 500);

    return () => clearTimeout(timer);
  }, [currentPrice]);

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
        {ltp ? (
          <span className={`price ${isIndexOrStock ? 'price-bold' : ''} ${flashClass}`}>{ltp.toFixed(2)}</span>
        ) : (
          <>
            <span className={`price bid ${flashClass}`}>{bestBid.toFixed(2)}</span>
            <span className="spread-mini">{spread.toFixed(2)}</span>
            <span className={`price ask ${flashClass}`}>{bestAsk.toFixed(2)}</span>
          </>
        )}
      </div>
    </div>
  );
});

TickerListItem.displayName = 'TickerListItem';
