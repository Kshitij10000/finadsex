import { useState, useEffect } from 'react';

export const MarketStatus = () => {
    const [time, setTime] = useState(new Date());
    const [isMarketOpen, setIsMarketOpen] = useState(false);

    useEffect(() => {
        const timer = setInterval(() => {
            const now = new Date();
            setTime(now);

            // Check Market Status (IST)
            // Market Open: Mon-Fri, 09:15 - 15:30
            const day = now.getDay(); // 0 = Sun, 6 = Sat
            const hours = now.getHours();
            const minutes = now.getMinutes();
            const currentMinutes = hours * 60 + minutes;

            const marketOpenMinutes = 9 * 60 + 15; // 09:15
            const marketCloseMinutes = 15 * 60 + 30; // 15:30

            const isWeekday = day >= 1 && day <= 5;
            const isTimeInRange = currentMinutes >= marketOpenMinutes && currentMinutes < marketCloseMinutes;

            setIsMarketOpen(isWeekday && isTimeInRange);
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    // Format time as HH:mm:ss
    const formatTime = (date) => {
        return date.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    return (
        <div className="market-status-container">
            <div className="market-time">
                {formatTime(time)}
            </div>
            <div className={`market-indicator ${isMarketOpen ? 'open' : 'closed'}`}>
                <span className="indicator-dot"></span>
                <span className="indicator-text">{isMarketOpen ? 'MARKET OPEN' : 'MARKET CLOSED'}</span>
            </div>
        </div>
    );
};
