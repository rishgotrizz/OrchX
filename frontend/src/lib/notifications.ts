import { toast as sonnerToast } from 'sonner';
import { eventBus } from './event-bus';

type ToastOptions = {
  description?: string;
  duration?: number;
  action?: { label: string; onClick: () => void };
};

export const notify = {
  success: (title: string, options?: ToastOptions) => {
    const id = sonnerToast.success(title, options);
    eventBus.emit('ui.notification.created', { id: String(id), type: 'success', title });
    return id;
  },
  error: (title: string, options?: ToastOptions) => {
    const id = sonnerToast.error(title, options);
    eventBus.emit('ui.notification.created', { id: String(id), type: 'error', title });
    return id;
  },
  info: (title: string, options?: ToastOptions) => {
    const id = sonnerToast.info(title, options);
    eventBus.emit('ui.notification.created', { id: String(id), type: 'info', title });
    return id;
  },
  warning: (title: string, options?: ToastOptions) => {
    const id = sonnerToast.warning(title, options);
    eventBus.emit('ui.notification.created', { id: String(id), type: 'warning', title });
    return id;
  },
  kernelAlert: (title: string, options?: ToastOptions) => {
    // High-priority toast style
    const id = sonnerToast(title, { 
      ...options, 
      className: 'bg-status-error/10 border-status-error text-status-error shadow-[0_0_20px_rgba(239,68,68,0.2)]',
    });
    eventBus.emit('ui.notification.created', { id: String(id), type: 'kernel', title });
    return id;
  }
};
