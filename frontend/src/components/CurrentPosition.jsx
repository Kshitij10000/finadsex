import { memo } from 'react';

export const CurrentPosition = memo(({ position }) => {
    if (!position || !position.active) {
        return (
            <div className="current-position-container empty">
                <div className="section-label">Current Position</div>
                <div className="no-position">No Active Position</div>
            </div>
        );
    }

    const { symbol, entry_price, quantity, type } = position;
    const displaySymbol = symbol?.split(':')[1] || symbol;
    const isBuy = type === 'BUY';

    return (
        <div className="current-position-container">
            <div className="section-label">Current Position</div>
            <div className="position-details">
                <div className="position-row">
                    <span className="label">Symbol</span>
                    <span className="value">{displaySymbol}</span>
                </div>
                <div className="position-row">
                    <span className="label">Type</span>
                    <span className={`value ${isBuy ? 'buy' : 'sell'}`}>{type}</span>
                </div>
                <div className="position-row">
                    <span className="label">Entry Price</span>
                    <span className="value">{entry_price?.toFixed(2)}</span>
                </div>
                <div className="position-row">
                    <span className="label">Quantity</span>
                    <span className="value">{quantity}</span>
                </div>
            </div>
        </div>
    );
});

CurrentPosition.displayName = 'CurrentPosition';
