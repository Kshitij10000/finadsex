import { useState, useMemo, useEffect } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { useWebSocket } from './hooks/useWebsocket';
import { ConnectionStatus } from './components/ConnectionStatus';
import { Settings } from './components/Settings';
import { TickerListItem } from './components/TickerListItem';
import { OrderBook } from './components/OrderBook';
import { OrderList } from './components/OrderList';
import { MarketStatus } from './components/MarketStatus';
import { CurrentPosition } from './components/CurrentPosition';
import { MarketBanner } from './components/MarketBanner';
import { IndicesTickerRow } from './components/IndicesTickerRow';
import './App.css';

// Backend URL
const WS_URL = 'ws://localhost:8000/ws/market_state';

const AppContent = () => {
  const { data, connectionStatus, error } = useWebSocket(WS_URL);
  const [selectedTicker, setSelectedTicker] = useState(null);
  const [allTickers, setAllTickers] = useState({});
  const [currentPosition, setCurrentPosition] = useState(null);
  const [positions, setPositions] = useState([]);

  // Process incoming WebSocket data
  useEffect(() => {
    if (!data) return;

    // Handle market_data (LTP updates)
    if (data.market_data) {
      setAllTickers(prev => {
        const next = { ...prev };
        Object.entries(data.market_data).forEach(([symbol, price]) => {
          next[symbol] = {
            ...next[symbol],
            symbol,
            ltp: price,
            // If we don't have depth yet, we might want to ensure the object exists
          };
        });
        return next;
      });
    }

    // Handle market_depth (Full depth updates)
    if (data.market_depth) {
      setAllTickers(prev => {
        const next = { ...prev };
        Object.entries(data.market_depth).forEach(([symbol, depthData]) => {
          next[symbol] = {
            ...next[symbol],
            ...depthData,
            symbol, // Ensure symbol is set
          };
        });
        return next;
      });
    }

    // Handle current_position
    if (data.current_position) {
      setCurrentPosition(data.current_position);
    }

    // Handle positions
    if (data.positions) {
      setPositions(data.positions);
    }

  }, [data]);

  // Convert map to array for rendering
  const tickers = useMemo(() => Object.values(allTickers), [allTickers]);

  // Organize tickers: Futures first, then CE, then PE, then Index/Others
  const organizedTickers = useMemo(() => {
    const futures = tickers.filter(t => t.symbol?.includes('FUT'));
    const ce = tickers.filter(t => t.symbol?.includes('CE'));
    const pe = tickers.filter(t => t.symbol?.includes('PE'));
    const others = tickers.filter(t => !t.symbol?.includes('FUT') && !t.symbol?.includes('CE') && !t.symbol?.includes('PE'));
    return { futures, ce, pe, others };
  }, [tickers]);

  // Get selected ticker data for order book
  const selectedTickerData = useMemo(() => {
    if (!selectedTicker) return null;
    return allTickers[selectedTicker];
  }, [selectedTicker, allTickers]);

  // Auto-select first Futures ticker on load if nothing selected
  useEffect(() => {
    if (!selectedTicker && organizedTickers.futures.length > 0) {
      setSelectedTicker(organizedTickers.futures[0].symbol);
    }
  }, [selectedTicker, organizedTickers.futures]);

  // Calculate Total Net PnL for Funds display
  const totalNetPnL = useMemo(() => {
    if (!positions || positions.length === 0) return 0;
    return positions.reduce((acc, pos) => acc + (pos.net_pnl || 0), 0);
  }, [positions]);

  const STARTING_FUNDS = 98562;
  const currentFunds = STARTING_FUNDS + totalNetPnL;

  return (
    <div className="app-minimal">
      <header className="app-header-minimal">
        <div className="app-name-small radium-text">FINADSEX</div>
        <div className="header-controls-minimal">
          <div className="funds-display">
            <div className="funds-group">
              <span className="funds-label-small">STARTING FUNDS</span>
              <span className="funds-value-small">{STARTING_FUNDS.toLocaleString('en-IN')}</span>
            </div>
            <div className="funds-divider"></div>
            <div className="funds-group">
              <span className="funds-label-small">CURRENT FUNDS</span>
              <span className="funds-value-highlight">{currentFunds.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</span>
            </div>
          </div>

          <div className="user-profile-interactive">
            <div className="user-avatar">KS</div>
            <div className="user-name">KSHITIJ DILIP SARVE</div>
            <div className="user-badge">PRO</div>
          </div>

          <MarketStatus />
          <ConnectionStatus status={connectionStatus} />
          <Settings />
        </div>
      </header>

      {error && (
        <div className="error-banner-minimal">
          {error}
        </div>
      )}

      <div className="app-layout">
        {/* Column 1: Indices & Stocks */}
        <aside className="sidebar-indices">
          <div className="indices-header">
            <span className="col-symbol">SYMBOL</span>
            <span className="col-last">LTP</span>
          </div>
          <div className="indices-list">
            {organizedTickers.others.map((ticker) => (
              <IndicesTickerRow key={ticker.symbol} ticker={ticker} />
            ))}
            {organizedTickers.others.length === 0 && (
              <div className="no-data-sidebar">Waiting...</div>
            )}
          </div>
        </aside>

        {/* Column 2: F&O (Futures, CE, PE) */}

        {/* Column 2: F&O (Futures, CE, PE) */}
        <aside className="sidebar-fno">
          {organizedTickers.futures.length > 0 && (
            <div className="ticker-section">
              <div className="section-label">Futures</div>
              {organizedTickers.futures.map((tickerData) => (
                <TickerListItem
                  key={tickerData.symbol}
                  tickerData={tickerData}
                  onSelect={() => setSelectedTicker(tickerData.symbol)}
                  isSelected={selectedTicker === tickerData.symbol}
                />
              ))}
            </div>
          )}

          {organizedTickers.ce.length > 0 && (
            <div className="ticker-section">
              <div className="section-label">CE</div>
              {organizedTickers.ce.map((tickerData) => (
                <TickerListItem
                  key={tickerData.symbol}
                  tickerData={tickerData}
                  onSelect={() => setSelectedTicker(tickerData.symbol)}
                  isSelected={selectedTicker === tickerData.symbol}
                />
              ))}
            </div>
          )}

          {organizedTickers.pe.length > 0 && (
            <div className="ticker-section">
              <div className="section-label">PE</div>
              {organizedTickers.pe.map((tickerData) => (
                <TickerListItem
                  key={tickerData.symbol}
                  tickerData={tickerData}
                  onSelect={() => setSelectedTicker(tickerData.symbol)}
                  isSelected={selectedTicker === tickerData.symbol}
                />
              ))}
            </div>
          )}
        </aside>

        {/* Column 3: Order Book */}
        {/* Column 3: Order Book */}
        <aside className="sidebar-orderbook">
          {selectedTickerData ? (
            <OrderBook
              bids={selectedTickerData.bids}
              asks={selectedTickerData.asks}
              bid_qty={selectedTickerData.bid_qty}
              ask_qty={selectedTickerData.ask_qty}
              symbol={selectedTickerData.symbol}
            />
          ) : (
            <div className="no-data-right">
              <p>Select a ticker</p>
            </div>
          )}
        </aside>

        {/* Column 4: All Orders */}
        <aside className="sidebar-orders">
          <OrderList />
        </aside>



        {/* Column 5: Current Position */}
        <aside className="sidebar-position">
          <CurrentPosition position={currentPosition} positions={positions} />
        </aside>
      </div>
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;