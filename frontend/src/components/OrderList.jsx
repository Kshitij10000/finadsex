import { memo, useEffect, useState, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebsocket';

// Backend URL for orders - adjust if needed
const ORDERS_WS_URL = 'ws://localhost:8000/ws/orders';

export const OrderList = memo(() => {
    const { data } = useWebSocket(ORDERS_WS_URL);
    const [orders, setOrders] = useState([]);
    const listRef = useRef(null);

    // Process incoming orders
    useEffect(() => {
        if (data) {
            setOrders(prev => {
                const incomingOrders = Array.isArray(data) ? data : [data];

                // Create a map of existing orders for easy deduplication
                const orderMap = new Map(prev.map(o => [o.order_id, o]));

                // Add/Update with incoming orders
                incomingOrders.forEach(o => {
                    if (o && o.order_id) {
                        orderMap.set(o.order_id, o);
                    }
                });

                // Convert back to array and sort by timestamp descending (latest first)
                const sortedOrders = Array.from(orderMap.values()).sort((a, b) => {
                    return (b.timestamp || 0) - (a.timestamp || 0);
                });

                return sortedOrders.slice(0, 50); // Keep last 50
            });
        }
    }, [data]);

    return (
        <div className="orderbook-container">
            <div className="section-label" style={{ padding: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
                All Orders
            </div>

            <div className="ob-header" style={{ gridTemplateColumns: '1fr 1fr 1fr 1fr' }}>
                <span>TIME</span>
                <span>SYMBOL</span>
                <span>ACTION</span>
                <span>PRICE</span>
            </div>

            <div className="ob-list" ref={listRef}>
                {orders.length === 0 && (
                    <div className="no-data-right">
                        <p>No executed orders</p>
                    </div>
                )}

                {orders.map((order) => {
                    const date = new Date(order.timestamp * 1000);
                    const timeStr = date.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
                    const isBuy = order.status === 'BUY' || order.type === 'BUY'; // Check both just in case

                    return (
                        <div key={order.order_id} className="ob-row" style={{ gridTemplateColumns: '1fr 1fr 1fr 1fr' }}>
                            <span className="ob-cell" style={{ textAlign: 'left', color: 'var(--text-tertiary)' }}>{timeStr}</span>
                            <span className="ob-cell" style={{ textAlign: 'left', fontWeight: '600' }}>{order.symbol?.split(':')[1] || order.symbol}</span>
                            <span className={`ob-cell ${isBuy ? 'price up' : 'price down'}`} style={{ textAlign: 'center' }}>
                                {order.status || order.type}
                            </span>
                            <span className="ob-cell price">{order.price?.toFixed(2)}</span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
});

OrderList.displayName = 'OrderList';
