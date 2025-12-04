import { useState, useEffect } from 'react';
import { usePing } from '../hooks/usePing';

export const MarketStatus = () => {
    const [time, setTime] = useState(new Date());
    const [isMarketOpen, setIsMarketOpen] = useState(false);
    const { latency, status } = usePing();

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

    const getPingColor = (ms) => {
        if (!ms) return 'var(--text-tertiary)';
        if (ms < 100) return 'var(--status-connected)'; // Green
        if (ms < 300) return '#fbbf24'; // Yellow/Orange
        return 'var(--status-error)'; // Red
    };

    const SignalIcon = ({ ms }) => {
        const color = getPingColor(ms);
        // 4 bars logic
        const bars = [
            ms !== null,           // Always show first bar if connected
            ms !== null && ms < 300,
            ms !== null && ms < 150,
            ms !== null && ms < 80
        ];

        return (
            <svg width="16" height="12" viewBox="0 0 16 12" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '4px' }}>
                <rect x="1" y="9" width="2" height="3" rx="1" fill={bars[0] ? color : 'var(--border-color)'} />
                <rect x="5" y="6" width="2" height="6" rx="1" fill={bars[1] ? color : 'var(--border-color)'} />
                <rect x="9" y="3" width="2" height="9" rx="1" fill={bars[2] ? color : 'var(--border-color)'} />
                <rect x="13" y="0" width="2" height="12" rx="1" fill={bars[3] ? color : 'var(--border-color)'} />
            </svg>
        );
    };

    return (
        <div className="market-status-container">
            <div className="ping-indicator" style={{
                marginRight: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                fontSize: '0.75rem',
                fontWeight: '500',
                color: 'var(--text-secondary)',
                background: 'rgba(255, 255, 255, 0.03)',
                padding: '4px 8px',
                borderRadius: '4px',
                border: '1px solid var(--border-color)'
            }}>
                <SignalIcon ms={status === 'Connected' ? latency : null} />
                <span style={{ fontFamily: 'var(--font-mono)', minWidth: '3ch', textAlign: 'right' }}>
                    {status === 'Connected' && latency !== null ? latency : '--'}
                </span>
                <span style={{ marginLeft: '2px', fontSize: '0.7em', opacity: 0.7 }}>ms</span>
            </div>
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
