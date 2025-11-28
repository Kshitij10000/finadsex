import { memo, useMemo, useEffect, useRef } from 'react';

export const OrderBook = memo(({ bids, asks, bid_qty, ask_qty, symbol }) => {
  const scrollContainerRef = useRef(null);
  const spreadRef = useRef(null);

  // Process Asks: Sort Descending (Highest Price First) -> Lowest Price Last (closest to spread)
  // Actually, standard vertical order books usually show:
  // Top: Asks (High -> Low)
  // Bottom: Bids (High -> Low)
  // This puts the spread in the middle.

  const processedAsks = useMemo(() => {
    if (!asks || !ask_qty) return [];
    const items = asks.map((price, idx) => ({
      price,
      qty: ask_qty[idx] || 0
    }));
    // Sort descending: Highest price at top, lowest (best ask) at bottom
    return items.sort((a, b) => b.price - a.price);
  }, [asks, ask_qty]);

  const processedBids = useMemo(() => {
    if (!bids || !bid_qty) return [];
    const items = bids.map((price, idx) => ({
      price,
      qty: bid_qty[idx] || 0
    }));
    // Sort descending: Highest price (best bid) at top, lowest at bottom
    return items.sort((a, b) => b.price - a.price);
  }, [bids, bid_qty]);

  // Auto-scroll to center (spread) when symbol changes or data loads
  useEffect(() => {
    if (spreadRef.current && scrollContainerRef.current) {
      // Scroll so the spread is in the middle of the container
      const container = scrollContainerRef.current;
      const spread = spreadRef.current;

      const containerHeight = container.clientHeight;
      const spreadTop = spread.offsetTop;

      // Center the spread: scrollTop = spreadTop - (containerHeight / 2)
      container.scrollTop = spreadTop - (containerHeight / 2);
    }
  }, [symbol, processedAsks.length, processedBids.length]);

  return (
    <div className="orderbook-container">
      <div className="ob-header">
        <span>BID QTY</span>
        <span>PRICE</span>
        <span>ASK QTY</span>
      </div>

      <div className="ob-list" ref={scrollContainerRef}>
        {/* Asks Section (Red) */}
        {processedAsks.map((item, idx) => (
          <div key={`ask-${idx}`} className="ob-row ask-row">
            <span className="ob-cell qty"></span>
            <span className="ob-cell price down">{item.price.toFixed(2)}</span>
            <span className="ob-cell qty">{item.qty.toLocaleString()}</span>
          </div>
        ))}

        {/* Spread Marker (Invisible target for scrolling) */}
        <div ref={spreadRef} style={{ height: 0, margin: 0, padding: 0 }} />

        {/* Bids Section (Green) */}
        {processedBids.map((item, idx) => (
          <div key={`bid-${idx}`} className="ob-row bid-row">
            <span className="ob-cell qty">{item.qty.toLocaleString()}</span>
            <span className="ob-cell price up">{item.price.toFixed(2)}</span>
            <span className="ob-cell qty"></span>
          </div>
        ))}
      </div>
    </div>
  );
});

OrderBook.displayName = 'OrderBook';