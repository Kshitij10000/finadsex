import { useState, useMemo, useEffect } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { useWebSocket } from './hooks/useWebsocket';
import { ConnectionStatus } from './components/ConnectionStatus';
import { Settings } from './components/Settings';
import { TickerListItem } from './components/TickerListItem';
import { OrderBook } from './components/OrderBook';
import { MarketStatus } from './components/MarketStatus';
import './App.css';

// Backend URL - adjust if needed
const WS_URL = 'ws://localhost:8000/ws/live-feed';

const AppContent = () => {
  const { data, connectionStatus, error } = useWebSocket(WS_URL);
  const [selectedTicker, setSelectedTicker] = useState(null);

  // Extract all tickers from the nested data structure
  const tickers = useMemo(() => {
    if (!data) return [];

    // Handle snapshot format: { type, tickers, data: { symbol: { tick_id, data: {...} } } }
    if (data.type === 'snapshot' && data.data) {
      return Object.entries(data.data).map(([symbol, tickerInfo]) => ({
        symbol,
        ...tickerInfo.data, // Extract the actual ticker data
        server_latencies: data.server_latencies,
        server_receive_time: data.server_receive_time,
        server_send_time: data.server_send_time,
      }));
    }

    // Handle single ticker format (backward compatibility)
    if (data.symbol) {
      return [data];
    }

    return [];
  }, [data]);

  // Organize tickers: Futures first, then CE, then PE
  const organizedTickers = useMemo(() => {
    const futures = tickers.filter(t => t.symbol?.includes('FUT'));
    const ce = tickers.filter(t => t.symbol?.includes('CE'));
    const pe = tickers.filter(t => t.symbol?.includes('PE'));
    return { futures, ce, pe };
  }, [tickers]);

  // Get selected ticker data for order book
  const selectedTickerData = useMemo(() => {
    if (!selectedTicker) return null;
    return tickers.find(t => t.symbol === selectedTicker);
  }, [selectedTicker, tickers]);

  // Auto-select first Futures ticker on load
  useEffect(() => {
    if (!selectedTicker && organizedTickers.futures.length > 0) {
      setSelectedTicker(organizedTickers.futures[0].symbol);
    }
  }, [selectedTicker, organizedTickers.futures]);

  return (
    <div className="app-minimal">
      <header className="app-header-minimal">
        <div className="app-name-small radium-text">FINADSEX</div>
        <div className="header-controls-minimal">
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
        <aside className="sidebar-left">
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

          {tickers.length === 0 && (
            <div className="no-data-sidebar">
              <p>Waiting for data...</p>
            </div>
          )}
        </aside>

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

        <main className="workspace-area">
          {/* Workspace area is empty for now */}
        </main>
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