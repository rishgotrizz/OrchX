import { z } from 'zod';

export interface ConfigurationSchema {
  id: string;
  label: string;
  description: string;
  category: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'color' | 'array' | 'object';
  defaultValue: any;
  validationSchema?: z.ZodTypeAny;
  options?: { label: string; value: string }[];
  searchKeywords: string[];
  restartRequired: boolean;
  experimental: boolean;
  visibility: 'public' | 'advanced' | 'hidden';
}

export interface ProviderMetadata {
  id: string;
  name: string;
  status: 'connected' | 'error' | 'disconnected';
  latencyMs: number;
  health: 'healthy' | 'degraded' | 'down';
  capabilities: string[];
  models: ModelMetadata[];
}

export interface ModelMetadata {
  id: string;
  name: string;
  providerId: string;
  contextLength: number;
  capabilities: string[];
}

export interface SettingsSession {
  currentCategory: string;
  currentProfile: string;
  searchQuery: string;
  modifiedSettings: Record<string, any>; // Tracks unsaved modifications
}
