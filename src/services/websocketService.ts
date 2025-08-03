import { toast } from 'sonner';

export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: string;
  user_id?: string;
  garden_id?: string;
}

export interface AgronomicUpdate {
  type: 'agronomic_update';
  garden_id: string;
  data: any;
  timestamp: string;
}

export interface OptimizationProgress {
  type: 'optimization_progress';
  progress: {
    generation: number;
    best_fitness: number;
    progress: number;
  };
  timestamp: string;
}

export interface ConflictAlert {
  type: 'conflict_alert';
  garden_id: string;
  conflicts: any;
  timestamp: string;
}

export interface IrrigationUpdate {
  type: 'irrigation_update';
  garden_id: string;
  irrigation_data: any;
  timestamp: string;
}

export interface ConnectionStats {
  total_connections: number;
  total_gardens: number;
  total_subscriptions: number;
  connection_metadata: Record<string, any>;
  garden_subscriptions: Record<string, string[]>;
}

export type WebSocketEvent = 
  | AgronomicUpdate 
  | OptimizationProgress 
  | ConflictAlert 
  | IrrigationUpdate
  | { type: 'connection_established' | 'subscription_confirmed' | 'unsubscription_confirmed' | 'pong' | 'error'; data?: any; timestamp?: string };

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isConnecting = false;
  private isConnected = false;
  private messageCallbacks: Map<string, (data: any) => void> = new Map();
  private eventListeners: Map<string, ((event: WebSocketEvent) => void)[]> = new Map();
  private pingInterval: NodeJS.Timeout | null = null;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || 'ws://localhost:8000';
  }

  public async connect(userId: string): Promise<void> {
    if (this.isConnecting || this.isConnected) {
      return;
    }

    this.isConnecting = true;

    try {
      const wsUrl = `${this.baseUrl.replace('http', 'ws')}/api/v1/agronomic/ws/agronomic-updates/${userId}`;
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.startPingInterval();
        this.emit('connected', { type: 'connected' });
      };

      this.socket.onmessage = (event) => {
        try {
          const message: WebSocketEvent = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.socket.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.isConnected = false;
        this.isConnecting = false;
        this.stopPingInterval();
        this.emit('disconnected', { type: 'disconnected', code: event.code, reason: event.reason });
        
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect(userId);
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', { type: 'error', error });
      };

    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.isConnecting = false;
      throw error;
    }
  }

  private scheduleReconnect(userId: string): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Scheduling WebSocket reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    this.reconnectTimeout = setTimeout(() => {
      this.connect(userId).catch(error => {
        console.error('Reconnect failed:', error);
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect(userId);
        } else {
          toast.error('Failed to reconnect to real-time updates');
        }
      });
    }, delay);
  }

  private startPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
    }

    this.pingInterval = setInterval(() => {
      if (this.isConnected && this.socket) {
        this.sendMessage({
          type: 'ping',
          timestamp: new Date().toISOString()
        });
      }
    }, 30000); // Ping every 30 seconds
  }

  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private handleMessage(message: WebSocketEvent): void {
    console.log('WebSocket message received:', message.type);
    
    // Emit to event listeners
    this.emit(message.type, message);
    
    // Handle specific message types
    switch (message.type) {
      case 'agronomic_update':
        this.handleAgronomicUpdate(message as AgronomicUpdate);
        break;
        
      case 'optimization_progress':
        this.handleOptimizationProgress(message as OptimizationProgress);
        break;
        
      case 'conflict_alert':
        this.handleConflictAlert(message as ConflictAlert);
        break;
        
      case 'irrigation_update':
        this.handleIrrigationUpdate(message as IrrigationUpdate);
        break;
        
      case 'connection_established':
        console.log('WebSocket connection established');
        break;
        
      case 'subscription_confirmed':
        console.log('Garden subscription confirmed:', message.data);
        break;
        
      case 'unsubscription_confirmed':
        console.log('Garden unsubscription confirmed:', message.data);
        break;
        
      case 'pong':
        // Ping response received
        break;
        
      case 'error':
        console.error('WebSocket error message:', message.data);
        toast.error(`Real-time error: ${message.data?.message || 'Unknown error'}`);
        break;
        
      default:
        console.warn('Unknown WebSocket message type:', message.type);
    }
  }

  private handleAgronomicUpdate(update: AgronomicUpdate): void {
    console.log('Agronomic update received for garden:', update.garden_id);
    // This will be handled by the specific components that are listening
  }

  private handleOptimizationProgress(progress: OptimizationProgress): void {
    console.log('Optimization progress:', progress.progress);
    // This will be handled by the optimization components
  }

  private handleConflictAlert(alert: ConflictAlert): void {
    console.log('Conflict alert received for garden:', alert.garden_id);
    toast.warning('Plant conflicts detected in your garden');
    // This will be handled by the garden editor components
  }

  private handleIrrigationUpdate(update: IrrigationUpdate): void {
    console.log('Irrigation update received for garden:', update.garden_id);
    // This will be handled by the irrigation components
  }

  public sendMessage(message: WebSocketMessage): void {
    if (!this.isConnected || !this.socket) {
      console.warn('WebSocket not connected, cannot send message');
      return;
    }

    try {
      this.socket.send(JSON.stringify(message));
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
    }
  }

  public subscribeToGarden(gardenId: string): void {
    this.sendMessage({
      type: 'subscribe_garden',
      garden_id: gardenId,
      timestamp: new Date().toISOString()
    });
  }

  public unsubscribeFromGarden(gardenId: string): void {
    this.sendMessage({
      type: 'unsubscribe_garden',
      garden_id: gardenId,
      timestamp: new Date().toISOString()
    });
  }

  public requestOptimization(plants: any[], zones: any[], constraints: any): void {
    this.sendMessage({
      type: 'request_optimization',
      data: {
        plants,
        zones,
        constraints
      },
      timestamp: new Date().toISOString()
    });
  }

  public getConnectionStats(): void {
    this.sendMessage({
      type: 'get_stats',
      timestamp: new Date().toISOString()
    });
  }

  public on(event: string, callback: (event: WebSocketEvent) => void): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);
  }

  public off(event: string, callback: (event: WebSocketEvent) => void): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: WebSocketEvent): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in WebSocket event listener:', error);
        }
      });
    }
  }

  public isConnectionActive(): boolean {
    return this.isConnected && this.socket?.readyState === WebSocket.OPEN;
  }

  public disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
    
    if (this.socket) {
      this.socket.close(1000, 'User initiated disconnect');
      this.socket = null;
    }
    
    this.isConnected = false;
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    
    console.log('WebSocket disconnected');
  }

  public getConnectionStatus(): {
    connected: boolean;
    connecting: boolean;
    reconnectAttempts: number;
    readyState: number | null;
  } {
    return {
      connected: this.isConnected,
      connecting: this.isConnecting,
      reconnectAttempts: this.reconnectAttempts,
      readyState: this.socket?.readyState || null
    };
  }
}

// Create singleton instance
export const websocketService = new WebSocketService();

// Export types
export type {
  WebSocketMessage,
  AgronomicUpdate,
  OptimizationProgress,
  ConflictAlert,
  IrrigationUpdate,
  ConnectionStats,
  WebSocketEvent
}; 