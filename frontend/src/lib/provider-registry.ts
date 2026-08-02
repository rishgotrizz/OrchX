import { ProviderMetadata } from './types/settings';

const REGISTRY = new Map<string, ProviderMetadata>();

export function registerProvider(provider: ProviderMetadata) {
  REGISTRY.set(provider.id, provider);
}

export function getAllProviders() {
  return Array.from(REGISTRY.values());
}
