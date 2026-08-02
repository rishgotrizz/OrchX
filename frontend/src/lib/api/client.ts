import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { eventBus } from '@/lib/event-bus';

export const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
});

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('orchx_jwt') : null;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => {
    eventBus.emit('ApiConnected');
    return response;
  },
  (error: AxiosError) => {
    eventBus.emit('ApiDisconnected');
    
    if (error.response?.status === 401) {
      eventBus.emit('AuthenticationChanged', { status: 'unauthorized' });
    }
    
    return Promise.reject(error);
  }
);
