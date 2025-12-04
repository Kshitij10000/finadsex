import { useState, useEffect, useRef } from 'react';

const PING_WS_URL = import.meta.env.VITE_WS_PING_URL || 'ws://localhost:8000/ws';

export const usePing = () => {
    const [latency, setLatency] = useState(null);
    const [status, setStatus] = useState('Disconnected');
    const wsRef = useRef(null);
    const timerRef = useRef(null);

    useEffect(() => {
        const connect = () => {
            const ws = new WebSocket(PING_WS_URL);
            wsRef.current = ws;

            ws.onopen = () => {
                setStatus('Connected');
                // Start pinging
                timerRef.current = setInterval(() => {
                    if (ws.readyState === WebSocket.OPEN) {
                        const start = Date.now();
                        ws.send(start.toString());
                    }
                }, 1000);
            };

            ws.onmessage = (event) => {
                const start = parseInt(event.data, 10);
                const end = Date.now();
                setLatency(end - start);
            };

            ws.onclose = () => {
                setStatus('Disconnected');
                setLatency(null);
                clearInterval(timerRef.current);
                // Reconnect after 3 seconds
                setTimeout(connect, 3000);
            };

            ws.onerror = (error) => {
                console.error('Ping WebSocket error:', error);
                ws.close();
            };
        };

        connect();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
            clearInterval(timerRef.current);
        };
    }, []);

    return { latency, status };
};
