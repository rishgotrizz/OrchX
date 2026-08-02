import { registerWidget } from "@/lib/widget-registry";
import { Settings, Sliders, Box, Network, Palette, Activity, Key, Shield, Lock, Server, Code, Eye } from "lucide-react";
import { SettingsNavigationWidget } from "./SettingsNavigationWidget";
import { SettingsEditorWidget } from "./SettingsEditorWidget";
import { ProviderManagerWidget } from "./ProviderManagerWidget";
import { ModelManagerWidget } from "./ModelManagerWidget";
import { ThemeManagerWidget } from "./ThemeManagerWidget";
import { SettingsDiagnosticsWidget } from "./SettingsDiagnosticsWidget";
import { registerSettingsCategory, registerConfiguration } from "@/lib/settings-registry";
import { registerProvider } from "@/lib/provider-registry";
import { z } from "zod";

const DEFAULT_MANIFEST = {
  version: "1.0.0",
  author: "OrchX Core",
  capabilities: ["read", "write"],
  permissions: ["settings"],
  refreshPolicy: "event" as const,
  category: "settings",
};

export function initializeSettingsWidgets() {
  registerWidget({ ...DEFAULT_MANIFEST, id: "settings-navigation", title: "Navigation", description: "Categories", icon: Settings, defaultSize: 40, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: SettingsNavigationWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "settings-editor", title: "Preferences", description: "Form Editor", icon: Sliders, defaultSize: 60, minSize: 40, preferredLayout: "horizontal", priority: "high", supportedLayouts: ["all"], component: SettingsEditorWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "provider-manager", title: "Providers", description: "API Status", icon: Box, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: ProviderManagerWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "model-manager", title: "Models", description: "Models List", icon: Network, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: ModelManagerWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "theme-manager", title: "Live Preview", description: "Appearance", icon: Palette, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: ThemeManagerWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "settings-diagnostics", title: "Diagnostics", description: "Health", icon: Activity, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "medium", supportedLayouts: ["all"], component: SettingsDiagnosticsWidget });
}

export function initializeSettingsMockData() {
  // Categories
  registerSettingsCategory({ id: 'providers', title: 'Provider Credentials', icon: Key, priority: 110 });
  registerSettingsCategory({ id: 'routing', title: 'LLM Routing & Resilience', icon: Network, priority: 100 });
  registerSettingsCategory({ id: 'security', title: 'Security & Sandbox Policies', icon: Lock, priority: 90 });
  registerSettingsCategory({ id: 'telemetry', title: 'Worker Pool & Telemetry', icon: Server, priority: 80 });
  registerSettingsCategory({ id: 'appearance', title: 'Appearance & UI Design', icon: Palette, priority: 70 });
  registerSettingsCategory({ id: 'editor', title: 'Workflow & Code Editor', icon: Sliders, priority: 60 });

  // 1. Provider Credentials & SecretVault
  registerConfiguration({
    id: 'providers.groq_key',
    label: 'Groq API Key',
    description: 'Ultra-low latency Groq LPU API key stored in SecretVault.',
    category: 'providers',
    type: 'string',
    defaultValue: 'gsk_... (AES-256-GCM Encrypted)',
    searchKeywords: ['groq', 'api key', 'secret', 'vault', 'lpu'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'providers.openrouter_key',
    label: 'OpenRouter API Key',
    description: 'Universal gateway API key accessing 330+ open and proprietary models.',
    category: 'providers',
    type: 'string',
    defaultValue: 'sk-or-v1-... (AES-256-GCM Encrypted)',
    searchKeywords: ['openrouter', 'api key', 'claude', 'gpt', 'models'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'providers.gemini_key',
    label: 'Google Gemini API Key',
    description: 'Google AI Studio API key for Gemini 1.5 Pro and 2.0 Flash models.',
    category: 'providers',
    type: 'string',
    defaultValue: 'AIzaSy... (AES-256-GCM Encrypted)',
    searchKeywords: ['gemini', 'google', 'api key', '1m context'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'providers.openai_key',
    label: 'OpenAI API Key',
    description: 'Direct OpenAI API key for GPT-4o, GPT-4o-mini, and o1 reasoning models.',
    category: 'providers',
    type: 'string',
    defaultValue: 'sk-proj-... (AES-256-GCM Encrypted)',
    searchKeywords: ['openai', 'gpt4', 'api key', 'o1'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'providers.vault_encryption',
    label: 'SecretVault AES-256-GCM Hardware Lock',
    description: 'Cryptographically seals all API credentials in SecretVault at rest.',
    category: 'providers',
    type: 'boolean',
    defaultValue: true,
    searchKeywords: ['encryption', 'vault', 'gcm', 'security'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  // 2. LLM Routing & Resilience
  registerConfiguration({
    id: 'routing.default_provider',
    label: 'Primary Execution Provider',
    description: 'Default LLM provider engine assigned for high-priority task routing.',
    category: 'routing',
    type: 'select',
    defaultValue: 'groq',
    options: [
      { label: 'Groq LPU (Ultra-fast 255ms)', value: 'groq' },
      { label: 'OpenRouter Universal (330+ Models)', value: 'openrouter' },
      { label: 'Google Gemini (1M Context)', value: 'gemini' },
      { label: 'OpenAI Direct', value: 'openai' }
    ],
    searchKeywords: ['provider', 'routing', 'groq', 'openrouter'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'routing.primary_model',
    label: 'Primary Reasoning Model',
    description: 'Default AI model utilized by Planner Agents for task breakdown.',
    category: 'routing',
    type: 'select',
    defaultValue: 'llama-3.1-8b-instant',
    options: [
      { label: 'llama-3.1-8b-instant (Groq LPU)', value: 'llama-3.1-8b-instant' },
      { label: 'meta-llama/llama-3.3-70b-instruct (OpenRouter)', value: 'meta-llama/llama-3.3-70b-instruct' },
      { label: 'claude-3.5-sonnet (Anthropic)', value: 'claude-3.5-sonnet' },
      { label: 'gpt-4o (OpenAI)', value: 'gpt-4o' }
    ],
    searchKeywords: ['model', 'llama', 'claude', 'gpt4'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'routing.temperature',
    label: 'Generation Temperature',
    description: 'Controls randomness in AI reasoning and code generation outputs.',
    category: 'routing',
    type: 'select',
    defaultValue: '0.2',
    options: [
      { label: '0.0 — Strict & Deterministic (Recommended for Code)', value: '0.0' },
      { label: '0.2 — Balanced Precision', value: '0.2' },
      { label: '0.7 — Creative Reasoning', value: '0.7' },
      { label: '1.0 — Exploratory / High Variance', value: '1.0' }
    ],
    searchKeywords: ['temperature', 'randomness', 'precision', 'code'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'routing.max_tokens',
    label: 'Maximum Token Limit',
    description: 'Upper bound on tokens generated per individual agent completion.',
    category: 'routing',
    type: 'select',
    defaultValue: '4096',
    options: [
      { label: '1,024 Tokens (Compact Answers)', value: '1024' },
      { label: '2,048 Tokens (Standard Completion)', value: '2048' },
      { label: '4,096 Tokens (Full Code Generation)', value: '4096' },
      { label: '8,192 Tokens (Extended Architecture Docs)', value: '8192' }
    ],
    searchKeywords: ['tokens', 'limit', 'max tokens', 'context'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'routing.circuit_breaker',
    label: 'Sub-Millisecond Circuit Breaker Failover',
    description: 'Automatically switches to secondary provider if primary API degrades or rate-limits.',
    category: 'routing',
    type: 'boolean',
    defaultValue: true,
    searchKeywords: ['circuit breaker', 'failover', 'resilience', 'fallback'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  // 3. Security & Sandbox Policies
  registerConfiguration({
    id: 'security.sandbox_mode',
    label: 'Plugin Sandbox Isolation Engine',
    description: 'Subsystem used to execute real-world tool plugins (Terminal, Python, Git).',
    category: 'security',
    type: 'select',
    defaultValue: 'subprocess',
    options: [
      { label: 'Subprocess Isolation (Standard Sandbox)', value: 'subprocess' },
      { label: 'Docker Container Sandbox (Zero-Host Access)', value: 'docker' },
      { label: 'Wasm Micro-VM Sandbox (Experimental)', value: 'wasm' }
    ],
    searchKeywords: ['sandbox', 'docker', 'subprocess', 'plugins'],
    restartRequired: true,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'security.command_guard',
    label: 'Destructive Pattern Guard',
    description: 'Blocks high-risk shell commands (sudo, rm -rf /, /sys modification).',
    category: 'security',
    type: 'boolean',
    defaultValue: true,
    searchKeywords: ['guard', 'command', 'sudo', 'block'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'security.audit_retention',
    label: 'Cryptographic Audit Log Retention',
    description: 'Duration to retain immutable SecretVault audit records on disk.',
    category: 'security',
    type: 'select',
    defaultValue: '30',
    options: [
      { label: '7 Days', value: '7' },
      { label: '30 Days (Recommended)', value: '30' },
      { label: '90 Days', value: '90' },
      { label: 'Indefinite / Permanent Retention', value: '0' }
    ],
    searchKeywords: ['audit', 'logs', 'retention', 'security'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  // 4. Worker Pool & Telemetry
  registerConfiguration({
    id: 'telemetry.max_workers',
    label: 'Maximum Worker Threads',
    description: 'Maximum concurrent LLM agent processes running in the Worker Pool.',
    category: 'telemetry',
    type: 'select',
    defaultValue: '8',
    options: [
      { label: '2 Active Workers (Lightweight)', value: '2' },
      { label: '4 Active Workers (Balanced)', value: '4' },
      { label: '8 Active Workers (High Performance)', value: '8' },
      { label: '16 Active Workers (Cluster Workload)', value: '16' }
    ],
    searchKeywords: ['workers', 'thread', 'concurrency', 'parallel'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'telemetry.heartbeat_frequency',
    label: 'Kernel Heartbeat Telemetry Rate',
    description: 'Frequency at which Runtime Observatory queries CPU, Memory, and Worker status.',
    category: 'telemetry',
    type: 'select',
    defaultValue: '5',
    options: [
      { label: '1s (Real-Time High Frequency)', value: '1' },
      { label: '5s (Standard Monitoring)', value: '5' },
      { label: '10s (Eco Mode)', value: '10' }
    ],
    searchKeywords: ['telemetry', 'heartbeat', 'frequency', 'cpu'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'telemetry.auto_recovery',
    label: 'Worker Self-Healing Auto-Recovery',
    description: 'Automatically restarts stalled or unresponsive worker processes.',
    category: 'telemetry',
    type: 'boolean',
    defaultValue: true,
    searchKeywords: ['auto-recovery', 'self-healing', 'worker', 'restart'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  // 5. Appearance & UI Design
  registerConfiguration({
    id: 'appearance.theme',
    label: 'Theme Palette',
    description: 'Select visual aesthetic color theme for the OrchX dashboard.',
    category: 'appearance',
    type: 'select',
    defaultValue: 'dark',
    options: [
      { label: 'Dark Midnight Void (Default)', value: 'dark' },
      { label: 'Cyberpunk Obsidian', value: 'cyberpunk' },
      { label: 'Minimal Glass', value: 'glass' }
    ],
    searchKeywords: ['theme', 'dark mode', 'color', 'aesthetic'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'appearance.density',
    label: 'UI Layout Density',
    description: 'Control spacing, padding, and size of studio panels.',
    category: 'appearance',
    type: 'select',
    defaultValue: 'comfortable',
    options: [
      { label: 'Compact (High Density)', value: 'compact' },
      { label: 'Comfortable (Standard)', value: 'comfortable' },
      { label: 'Spacious (Large Touch Targets)', value: 'spacious' }
    ],
    searchKeywords: ['density', 'spacing', 'size', 'layout'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'appearance.glow_effects',
    label: 'Dynamic Micro-Animations & Glow Effects',
    description: 'Enable dynamic visual glow highlights on active node connections.',
    category: 'appearance',
    type: 'boolean',
    defaultValue: true,
    searchKeywords: ['glow', 'animation', 'micro-animation', 'ui'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  // 6. Workflow & Code Editor
  registerConfiguration({
    id: 'editor.autoSave',
    label: 'Auto Save Workflows & Documents',
    description: 'Automatically persist edits to SQLite memory engine after 1.5 seconds.',
    category: 'editor',
    type: 'boolean',
    defaultValue: true,
    searchKeywords: ['save', 'auto', 'editor', 'sqlite'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  registerConfiguration({
    id: 'editor.live_tracer',
    label: 'Live Latency Tracer Logging',
    description: 'Stream sub-second node execution logs directly inside Workflow Forge.',
    category: 'editor',
    type: 'boolean',
    defaultValue: true,
    searchKeywords: ['tracer', 'live log', 'stream', 'latency'],
    restartRequired: false,
    experimental: false,
    visibility: 'public'
  });

  // Providers Registry Initial Mock Setup
  registerProvider({
    id: 'groq',
    name: 'Groq LPU',
    status: 'connected',
    latencyMs: 255,
    health: 'healthy',
    capabilities: ['chat', 'completion'],
    models: [
      { id: 'llama-3.1-8b-instant', name: 'Llama 3.1 8B Instant (Ultra-fast)', providerId: 'groq', contextLength: 8192, capabilities: ['fast'] },
      { id: 'llama-3.3-70b-versatile', name: 'Llama 3.3 70B Versatile', providerId: 'groq', contextLength: 128000, capabilities: ['reasoning'] }
    ]
  });

  registerProvider({
    id: 'openrouter',
    name: 'OpenRouter Universal',
    status: 'connected',
    latencyMs: 1970,
    health: 'healthy',
    capabilities: ['chat', 'completion', 'vision'],
    models: [
      { id: 'meta-llama/llama-3.1-8b-instruct', name: 'Llama 3.1 8B Instruct', providerId: 'openrouter', contextLength: 128000, capabilities: ['coding'] },
      { id: 'meta-llama/llama-3.3-70b-instruct', name: 'Llama 3.3 70B Instruct', providerId: 'openrouter', contextLength: 128000, capabilities: ['reasoning'] }
    ]
  });

  registerProvider({
    id: 'gemini',
    name: 'Google Gemini',
    status: 'connected',
    latencyMs: 280,
    health: 'healthy',
    capabilities: ['chat', 'vision', 'tool_calling'],
    models: [
      { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro (1M Context)', providerId: 'gemini', contextLength: 1000000, capabilities: ['vision', 'long-context'] }
    ]
  });
}
