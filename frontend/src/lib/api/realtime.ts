import { eventBus } from '@/lib/event-bus';

export class RealtimeEngine {
  private ws: WebSocket | null = null;
  private sse: EventSource | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor(url: string = 'ws://localhost:8000/api/v1/ws') {
    this.url = url;
  }

  connect() {
    if (this.ws || typeof window === 'undefined') return;
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        eventBus.emit('RealtimeConnected');
      };

      this.ws.onclose = () => {
        this.ws = null;
        eventBus.emit('RealtimeDisconnected');
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => this.connect(), Math.min(1000 * 2 ** this.reconnectAttempts++, 10000));
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type && data.payload) {
            eventBus.emit(data.type, data.payload);
          }
        } catch (e) {
          console.error('Failed to parse realtime message', e);
        }
      };
    } catch (e) {
      console.warn("RealtimeEngine failed to connect WebSocket. Fallback/Mock mode active.");
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  subscribe(channel: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'subscribe', channel }));
    }
  }

  unsubscribe(channel: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'unsubscribe', channel }));
    }
  }
}

export const realtimeEngine = new RealtimeEngine();
