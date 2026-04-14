import { useState, useEffect, useRef, useCallback } from 'react';

interface WebSocketOptions {
    url: string;
    onOpen?: () => void;
    onClose?: () => void;
    onMessage?: (event: MessageEvent) => void;
    onError?: (event: Event) => void;
    reconnectAttempts?: number;
    reconnectInterval?: number;
}

/**
 * Manages a single WebSocket connection tied to a URL.
 * Reconnects only when the URL changes (thread switch) or on
 * unexpected disconnects. Callbacks are stored in refs so they
 * never cause spurious reconnections when React re-renders.
 * 
 */
export const useWebSocket = ({
    url,
    onOpen,
    onClose,
    onMessage,
    onError,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
}: WebSocketOptions) => {
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState<Event | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectCount = useRef(0);
    const reconnectTimer = useRef<NodeJS.Timeout>();
    const intentionalClose = useRef(false);

    const onMessageRef = useRef(onMessage);
    const onOpenRef = useRef(onOpen);
    const onCloseRef = useRef(onClose);
    const onErrorRef = useRef(onError);

    useEffect(() => { onMessageRef.current = onMessage; }, [onMessage]);
    useEffect(() => { onOpenRef.current = onOpen; }, [onOpen]);
    useEffect(() => { onCloseRef.current = onClose; }, [onClose]);
    useEffect(() => { onErrorRef.current = onError; }, [onError]);

    const connect = useCallback(() => {
        intentionalClose.current = false;

        try {
            const ws = new WebSocket(url);

            ws.onopen = () => {
                setIsConnected(true);
                setError(null);
                reconnectCount.current = 0;
                onOpenRef.current?.();
            };

            ws.onclose = () => {
                setIsConnected(false);
                onCloseRef.current?.();

                if (!intentionalClose.current && reconnectCount.current < reconnectAttempts) {
                    reconnectTimer.current = setTimeout(() => {
                        reconnectCount.current += 1;
                        connect();
                    }, reconnectInterval);
                }
            };

            ws.onmessage = (event) => {
                onMessageRef.current?.(event);
            };

            ws.onerror = (event) => {
                setError(event);
                onErrorRef.current?.(event);
            };

            wsRef.current = ws;
        } catch (err) {
            console.error("WebSocket connection error:", err);
        }
    }, [url, reconnectAttempts, reconnectInterval]);

    useEffect(() => {
        connect();

        return () => {
            intentionalClose.current = true;
            if (reconnectTimer.current) {
                clearTimeout(reconnectTimer.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect]);

    const sendMessage = useCallback((data: any) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
            return true;
        }
        return false;
    }, []);

    return {
        sendMessage,
        isConnected,
        error,
    };
};
