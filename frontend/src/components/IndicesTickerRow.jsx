import { memo, useEffect, useRef, useState } from 'react';

export const IndicesTickerRow = memo(({ ticker }) => {
    const [flashClass, setFlashClass] = useState('');
    const prevPriceRef = useRef(ticker.ltp);

    useEffect(() => {
        const currentPrice = ticker.ltp;
        const prevPrice = prevPriceRef.current;

        if (currentPrice !== prevPrice) {
            if (currentPrice > prevPrice) {
                setFlashClass('flash-up');
            } else if (currentPrice < prevPrice) {
                setFlashClass('flash-down');
            }

            // Update ref
            prevPriceRef.current = currentPrice;

            // Clear flash after animation
            const timer = setTimeout(() => {
                setFlashClass('');
            }, 800); // Match animation duration

            return () => clearTimeout(timer);
        }
    }, [ticker.ltp]);

    return (
        <div className="indices-row">
            <span className="col-symbol">{ticker.symbol?.split(':')[1] || ticker.symbol}</span>
            <span className={`col-last ${flashClass}`}>{ticker.ltp?.toFixed(2)}</span>
        </div>
    );
});

IndicesTickerRow.displayName = 'IndicesTickerRow';
