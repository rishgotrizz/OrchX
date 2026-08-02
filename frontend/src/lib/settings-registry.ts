import { ConfigurationSchema } from './types/settings';
import { LucideIcon } from 'lucide-react';

export interface SettingsCategoryMetadata {
  id: string;
  title: string;
  icon: LucideIcon;
  priority: number;
}

const CATEGORY_REGISTRY = new Map<string, SettingsCategoryMetadata>();
const CONFIG_REGISTRY = new Map<string, ConfigurationSchema>();

export function registerSettingsCategory(category: SettingsCategoryMetadata) { 
  CATEGORY_REGISTRY.set(category.id, category); 
}

export function registerConfiguration(config: ConfigurationSchema) { 
  CONFIG_REGISTRY.set(config.id, config); 
}

export function getCategories() { 
  return Array.from(CATEGORY_REGISTRY.values()).sort((a, b) => b.priority - a.priority); 
}

export function getConfigurationsByCategory(categoryId: string) { 
  return Array.from(CONFIG_REGISTRY.values()).filter(c => c.category === categoryId); 
}

export function getAllConfigurations() {
  return Array.from(CONFIG_REGISTRY.values());
}

export function searchConfigurations(query: string) { 
  const lowerQuery = query.toLowerCase();
  return Array.from(CONFIG_REGISTRY.values()).filter(c => 
    c.label.toLowerCase().includes(lowerQuery) || 
    c.description.toLowerCase().includes(lowerQuery) ||
    c.searchKeywords.some(k => k.toLowerCase().includes(lowerQuery))
  ); 
}
