import { useQuery } from '@tanstack/react-query';
import { ProviderRepository } from '@/lib/repositories/ProviderRepository';
import { QueryKeys } from '@/lib/repositories/QueryKeys';
import { ProviderMetadata } from '@/lib/types/settings';
import { useEffect } from 'react';
import { registerProvider, getAllProviders } from '@/lib/provider-registry';

export function useProviders() {
  const { data: providers = [], isLoading, error } = useQuery({
    queryKey: QueryKeys.providers.all,
    queryFn: ProviderRepository.getAll
  });

  // Keep the registry in sync for legacy non-React consumers
  useEffect(() => {
    if (providers.length > 0) {
      providers.forEach(p => registerProvider(p));
    }
  }, [providers]);

  return { providers, isLoading, error };
}
