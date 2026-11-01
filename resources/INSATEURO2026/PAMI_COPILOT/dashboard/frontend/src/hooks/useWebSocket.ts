import { useState, useEffect, useCallback, useRef } from 'react';
import type { WSMessage, ConnectionStatus } from '../types/telemetry';

interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: WSMessage) => void;
  reconnectDelay?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  status: ConnectionStatus | null;
  send: (data: object) => void;
  reconnect: () => void;
}

export function useWebSocket({
  url,
  onMessage,
  reconnectDelay = 2000,
}: UseWebSocketOptions): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [status, setStatus] = useState<ConnectionStatus | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[WS] Connected');
        setIsConnected(true);
      };

      ws.onclose = () => {
        console.log('[WS] Disconnected');
        setIsConnected(false);
        wsRef.current = null;
        
        // Auto-reconnect
        reconnectTimeoutRef.current = window.setTimeout(() => {
          console.log('[WS] Reconnecting...');
          connect();
        }, reconnectDelay);
      };

      ws.onerror = (error) => {
        console.error('[WS] Error:', error);
      };

      ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);
          
          // Handle status updates internally
          if (message.type === 'status') {
            setStatus(message.data);
          }
          
          // Handle ping with pong
          if (message.type === 'ping') {
            ws.send(JSON.stringify({ type: 'pong' }));
            return;
          }

          // Forward to callback
          onMessage?.(message);
        } catch (e) {
          console.error('[WS] Parse error:', e);
        }
      };
    } catch (e) {
      console.error('[WS] Connection error:', e);
    }
  }, [url, onMessage, reconnectDelay]);

  const send = useCallback((data: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  const reconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
    }
    connect();
  }, [connect]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { isConnected, status, send, reconnect };
}
