import { eventBus } from '@/lib/event-bus';

export type LogLevel = 'trace' | 'debug' | 'info' | 'warn' | 'error' | 'critical';

export interface TelemetryAdapter {
  name: string;
  log: (level: LogLevel, message: string, data?: any) => void;
  trackError: (error: Error, context?: any) => void;
}

// Default Console Adapter
export const ConsoleAdapter: TelemetryAdapter = {
  name: 'ConsoleAdapter',
  log: (level, message, data) => {
    if (process.env.NODE_ENV === 'production' && ['trace', 'debug'].includes(level)) return;
    
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
    
    switch (level) {
      case 'trace':
      case 'debug': console.debug(prefix, message, data || ''); break;
      case 'info': console.info(prefix, message, data || ''); break;
      case 'warn': console.warn(prefix, message, data || ''); break;
      case 'error': 
      case 'critical': console.error(prefix, message, data || ''); break;
    }
  },
  trackError: (error, context) => {
    console.error(`[ERROR TRACKED]`, error, context);
  }
};

class TelemetryEngine {
  private adapters: TelemetryAdapter[] = [ConsoleAdapter];

  registerAdapter(adapter: TelemetryAdapter) {
    this.adapters.push(adapter);
  }

  log(level: LogLevel, message: string, data?: any) {
    this.adapters.forEach(a => a.log(level, message, data));
  }

  trackError(error: Error, context?: any) {
    this.adapters.forEach(a => a.trackError(error, context));
    eventBus.emit('GPUOverloaded'); // Could trigger fallback UI generically if needed, but typically you map specific errors
  }
}

export const telemetry = new TelemetryEngine();
