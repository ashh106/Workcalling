const WS_URL = 'ws://localhost:8000/ws/chat';

export interface ChatMessage {
  role: string;
  content: string;
  [key: string]: unknown;
}

export interface WsMessage {
  type: string;
  content?: string;
  messages?: ChatMessage[];
  tool?: string;
  args?: Record<string, unknown>;
}

export class ChatService {
  private socket: WebSocket | null = null;
  private onMessage: (msg: WsMessage) => void;
  private onConnectionChange: (connected: boolean) => void;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    onMessage: (msg: WsMessage) => void,
    onConnectionChange: (connected: boolean) => void
  ) {
    this.onMessage = onMessage;
    this.onConnectionChange = onConnectionChange;
  }

  connect() {
    if (this.socket?.readyState === WebSocket.OPEN) return;
    
    console.log('Attempting WebSocket connection to:', WS_URL);
    this.socket = new WebSocket(WS_URL);

    this.socket.onopen = () => {
      console.log('WebSocket Connected!');
      this.onConnectionChange(true);
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WS Received:', data);
        this.onMessage(data);
      } catch (e) {
        console.error('Failed to parse WS message:', e);
      }
    };

    this.socket.onclose = () => {
      console.log('WebSocket Disconnected, retrying in 2s...');
      this.onConnectionChange(false);
      this.socket = null;
      this.reconnectTimer = setTimeout(() => this.connect(), 2000);
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };
  }

  sendMessage(messages: ChatMessage[]) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      console.log('WS Sending:', { messages });
      this.socket.send(JSON.stringify({ messages }));
    } else {
      console.error('Cannot send message, WebSocket is not open. Current state:', this.socket?.readyState);
    }
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
