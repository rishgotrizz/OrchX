import mitt from 'mitt';

type PanelEvents = {
  'ui.panel.opened': { panelId: string };
  'ui.panel.closed': { panelId: string };
  'ui.panel.resized': { panelId: string; size: number };
  'ui.panel.collapsed': { panelId: string };
  'ui.panel.expanded': { panelId: string };
  'ui.panel.focused': { panelId: string };
  'ui.panel.blurred': { panelId: string };
  'ui.panel.fullscreen': { panelId: string };
  'ui.panel.restored': { panelId: string };
};

type WorkspaceEvents = {
  'ui.workspace.changed': { workspaceId: string };
  'ui.command.executed': { commandId: string; source: string };
  'ui.notification.created': { id: string; type: string; title: string };
};

type RuntimeEvents = {
  KernelStarted: void;
  KernelStopped: void;
  KernelOnline: void;
  KernelOffline: void;
  WorkflowStarted: { workflowId: string };
  WorkflowCompleted: { workflowId: string };
  ExecutionStarted: { executionId: string };
  ExecutionPaused: { executionId: string };
  ExecutionResumed: { executionId: string };
  ExecutionCompleted: { executionId: string };
  ExecutionFailed: { executionId: string; error: string };
  TaskQueued: { taskId: string };
  TaskStarted: { taskId: string };
  TaskFinished: { taskId: string };
  TaskFailed: { taskId: string; error: string };
  WorkerSpawned: { workerId: string };
  WorkerDestroyed: { workerId: string };
  AgentSpawned: { agentId: string };
  AgentStopped: { agentId: string };
  ProviderConnected: { providerId: string };
  ProviderDisconnected: { providerId: string };
  ProviderRecovered: { providerId: string };
  ProviderFailed: { providerId: string; error: string };
  ProviderRateLimited: { providerId: string };
  ProviderTimeout: { providerId: string };
  MemoryUpdated: { usage: number };
  QueueOverflow: { queueId: string };
  CreditsUpdated: { used: number; limit: number };
  PluginInstalled: { pluginId: string };
};

type PreviewEvents = {
  ArtifactGenerated: { artifactId: string };
  ArtifactUpdated: { artifactId: string };
  ArtifactDeleted: { artifactId: string };
  PreviewOpened: { artifactId: string; version?: number };
  PreviewClosed: { artifactId: string };
  RendererChanged: { rendererId: string };
  ExportStarted: { format: string };
  ExportCompleted: { url: string };
};

type DocumentEvents = {
  DocumentCreated: { documentId: string };
  DocumentOpened: { documentId: string };
  DocumentSaved: { documentId: string };
  DocumentClosed: { documentId: string };
  DocumentDeleted: { documentId: string };
  DocumentMoved: { documentId: string; newFolderId: string };
  DocumentShared: { documentId: string };
  DocumentExported: { documentId: string; format: string };
  SearchStarted: { query: string };
  SearchCompleted: { resultsCount: number };
  VersionRestored: { documentId: string; version: number };
  KnowledgeUpdated: { nodeId: string };
};

type SettingsEvents = {
  SettingsChanged: { key: string; value: any };
  ThemeChanged: { themeId: string };
  ProviderEnabled: { providerId: string };
  ProviderDisabled: { providerId: string };
  ModelChanged: { modelId: string };
  ShortcutUpdated: { shortcutId: string };
  ProfileImported: { profileId: string };
  ProfileExported: { profileId: string };
  PluginConfigured: { pluginId: string };
  WorkspaceChanged: { workspaceId: string };
  PreferenceReset: { key: string };
  FeatureFlagChanged: { flagId: string; enabled: boolean };
  ConfigurationUpdated: void;
};

type NetworkEvents = {
  ApiConnected: void;
  ApiDisconnected: void;
  AuthenticationChanged: { status: 'authorized' | 'unauthorized' };
  RealtimeConnected: void;
  RealtimeDisconnected: void;
  DocumentSynced: { documentId: string };
  ArtifactSynced: { artifactId: string };
  ProviderUpdated: { providerId: string };
  ModelDiscovered: { modelId: string };
  CacheUpdated: { key: string };
  UploadCompleted: { fileId: string };
  DownloadCompleted: { fileId: string };
};

type ExperienceEvents = {
  SceneLoaded: { sceneId: string };
  SceneUnloaded: { sceneId: string };
  AnimationStarted: { id: string };
  AnimationCompleted: { id: string };
  BackgroundChanged: { bgId: string };
  PerformanceModeChanged: { mode: string };
  ReducedMotionEnabled: void;
  GPUOverloaded: void;
  RenderQualityChanged: { quality: string };
  ExperienceProfileChanged: { profile: string };
};

export type EventBusMap = PanelEvents & WorkspaceEvents & RuntimeEvents & PreviewEvents & DocumentEvents & SettingsEvents & NetworkEvents & ExperienceEvents;

export const eventBus = mitt<EventBusMap>();
