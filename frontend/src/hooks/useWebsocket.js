import { useEffect, useRef, useState, useCallback } from 'react';

export const useWebSocket = (url) => {
  const [data, setData] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      setConnectionStatus('Connecting...');
      const ws = new WebSocket(url);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('Connected');
        setError(null);
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setData(parsed);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        setError('WebSocket connection error');
        setConnectionStatus('Error');
      };

      ws.onclose = () => {
        setConnectionStatus('Disconnected');
        wsRef.current = null;
        
        // Auto-reconnect with exponential backoff
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectAttempts.current++;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };

      wsRef.current = ws;
    } catch (err) {
      setError(err.message);
      setConnectionStatus('Error');
    }
  }, [url]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnectionStatus('Disconnected');
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return { data, connectionStatus, error, reconnect: connect, disconnect };
};