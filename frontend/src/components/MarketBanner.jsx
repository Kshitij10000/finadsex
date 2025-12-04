import { memo } from 'react';
import './MarketBanner.css';

export const MarketBanner = memo(({ tickers }) => {
    if (!tickers || tickers.length === 0) return null;

    return (
        <div className="market-banner-container">
            <div className="market-banner-track">
                {/* Duplicate the list to ensure smooth infinite scrolling */}
                {[...tickers, ...tickers].map((ticker, index) => (
                    <div key={`${ticker.symbol}-${index}`} className="banner-item">
                        <span className="banner-symbol">{ticker.symbol?.split(':')[1] || ticker.symbol}</span>
                        <span className="banner-price">{ticker.ltp?.toFixed(2)}</span>
                        {/* Calculate change if available, otherwise just show price */}
                    </div>
                ))}
            </div>
        </div>
    );
});

MarketBanner.displayName = 'MarketBanner';
