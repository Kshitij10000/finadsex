import { memo, useMemo } from 'react';

export const CurrentPosition = memo(({ position, positions }) => {
    const hasActivePosition = position && position.active;
    const hasPositions = positions && positions.length > 0;

    if (!hasActivePosition && !hasPositions) {
        return (
            <div className="current-position-container empty">
                <div className="section-label">Current Position</div>
                <div className="no-position">No Active Position</div>
            </div>
        );
    }

    const formatSymbol = (sym) => sym?.split(':')[1] || sym;

    const totals = useMemo(() => {
        if (!positions || positions.length === 0) return null;
        return positions.reduce((acc, pos) => ({
            gross: acc.gross + (pos.gross_pnl || 0),
            charges: acc.charges + (pos.total_charges || 0),
            net: acc.net + (pos.net_pnl || 0)
        }), { gross: 0, charges: 0, net: 0 });
    }, [positions]);

    return (
        <div className="current-position-container">
            <div className="section-label">Current Position</div>
            <div className="active-position-wrapper">
                {hasActivePosition ? (
                    <div className="position-details">
                        <div className="position-row">
                            <span className="label">Symbol</span>
                            <span className="value">{formatSymbol(position.symbol)}</span>
                        </div>
                        <div className="position-row">
                            <span className="label">Type</span>
                            <span className={`value ${position.type === 'BUY' ? 'buy' : 'sell'}`}>{position.type}</span>
                        </div>
                        <div className="position-row">
                            <span className="label">Entry Price</span>
                            <span className="value">{position.price?.toFixed(2)}</span>
                        </div>
                        <div className="position-row">
                            <span className="label">Quantity</span>
                            <span className="value">{position.quantity}</span>
                        </div>
                    </div>
                ) : (
                    <div className="no-position">No Active Position</div>
                )}
            </div>

            {hasPositions && (
                <>
                    <div className="section-divider"></div>
                    <div className="section-label">Positions History</div>

                    {totals && (
                        <div className="golden-summary-card">
                            <div className="position-row">
                                <span className="label golden-text" style={{ fontWeight: 'bold' }}>Total Gross PnL</span>
                                <span className={`value ${totals.gross >= 0 ? 'buy' : 'sell'}`} style={{ fontWeight: 'bold' }}>
                                    {totals.gross.toFixed(2)}
                                </span>
                            </div>
                            <div className="position-row">
                                <span className="label golden-text" style={{ fontWeight: 'bold' }}>Total Charges</span>
                                <span className="value sell" style={{ fontWeight: 'bold' }}>
                                    {totals.charges.toFixed(2)}
                                </span>
                            </div>
                            <div className="position-row" style={{ borderTop: '1px dashed rgba(255, 215, 0, 0.3)', paddingTop: '0.25rem', marginTop: '0.25rem' }}>
                                <span className="label golden-text" style={{ fontWeight: 'bold', fontSize: '1rem' }}>Total Net PnL</span>
                                <span className={`value ${totals.net >= 0 ? 'buy' : 'sell'}`} style={{ fontWeight: 'bold', fontSize: '1.1rem', textShadow: '0 0 10px rgba(0,0,0,0.5)' }}>
                                    {totals.net.toFixed(2)}
                                </span>
                            </div>
                        </div>
                    )}

                    <div className="positions-list">
                        {positions.map((pos, index) => {
                            const pnlClass = pos.net_pnl >= 0 ? 'buy' : 'sell';
                            return (
                                <div key={index} className="position-item">
                                    <div className="position-row">
                                        <span className="label">Symbol</span>
                                        <span className="value">{formatSymbol(pos.Symbol)}</span>
                                    </div>
                                    <div className="position-row">
                                        <span className="label">Qty</span>
                                        <span className="value">{pos.quantity}</span>
                                    </div>
                                    <div className="position-row">
                                        <span className="label">Entry/Exit</span>
                                        <span className="value">{pos.entry_price?.toFixed(2)} / {pos.exit_price?.toFixed(2)}</span>
                                    </div>
                                    <div className="position-row">
                                        <span className="label">Gross PnL</span>
                                        <span className={`value ${pos.gross_pnl >= 0 ? 'buy' : 'sell'}`}>{pos.gross_pnl?.toFixed(2)}</span>
                                    </div>
                                    <div className="position-row">
                                        <span className="label">Tax/Chg</span>
                                        <span className="value sell">{pos.total_charges?.toFixed(2)}</span>
                                    </div>
                                    <div className="position-row">
                                        <span className="label">Net PnL</span>
                                        <span className={`value ${pnlClass}`}>{pos.net_pnl?.toFixed(2)}</span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </>
            )}
        </div>
    );
});

CurrentPosition.displayName = 'CurrentPosition';
