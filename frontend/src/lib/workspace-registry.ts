import { 
  LayoutDashboard, 
  Activity, 
  MonitorPlay, 
  FileText, 
  Workflow, 
  FolderGit2, 
  Settings,
  LucideIcon
} from "lucide-react";

export type WorkspaceStatus = 'active' | 'beta' | 'deprecated' | 'upcoming';

export interface WorkspaceConfig {
  id: string;
  title: string;
  route: string;
  icon: LucideIcon;
  description: string;
  shortcut: string;
  badge?: string;
  status: WorkspaceStatus;
  permissions: string[];
  featureFlags: string[];
}

export const WORKSPACE_REGISTRY: WorkspaceConfig[] = [
  {
    id: "mission-control",
    title: "Mission Control",
    route: "/mission-control",
    icon: LayoutDashboard,
    description: "Central command for all active tasks and AI worker status.",
    shortcut: "⌘1",
    status: "active",
    permissions: ["workspace:read"],
    featureFlags: []
  },
  {
    id: "runtime-observatory",
    title: "Runtime Observatory",
    route: "/runtime-observatory",
    icon: Activity,
    description: "Live telemetry and performance metrics for the AI kernel.",
    shortcut: "⌘2",
    status: "active",
    permissions: ["telemetry:read"],
    featureFlags: []
  },
  {
    id: "preview-studio",
    title: "Preview Studio",
    route: "/preview-studio",
    icon: MonitorPlay,
    description: "Side-by-side live rendering of artifacts and generation logs.",
    shortcut: "⌘3",
    status: "active",
    permissions: ["artifacts:read"],
    featureFlags: ["render-engine-v2"]
  },
  {
    id: "documents-studio",
    title: "Documents Studio",
    route: "/documents-studio",
    icon: FileText,
    description: "Collaborative rich text editing with inline AI assistance.",
    shortcut: "⌘4",
    status: "active",
    permissions: ["documents:read", "documents:write"],
    featureFlags: []
  },
  {
    id: "workflow-forge",
    title: "Workflow Forge",
    route: "/workflow-forge",
    icon: Workflow,
    description: "Node-based visual builder for multi-agent workflows.",
    shortcut: "⌘5",
    status: "active",
    permissions: ["workflows:read", "workflows:write"],
    featureFlags: []
  },
  {
    id: "project-vault",
    title: "Project Vault",
    route: "/project-vault",
    icon: FolderGit2,
    description: "Secure storage for all project files, secrets, and environment state.",
    shortcut: "⌘6",
    status: "active",
    permissions: ["projects:read"],
    featureFlags: []
  },
  {
    id: "command-center",
    title: "Command Center",
    route: "/command-center",
    icon: Settings,
    description: "Global settings, billing, and provider configuration.",
    shortcut: "⌘7",
    status: "active",
    permissions: ["settings:read"],
    featureFlags: []
  }
];

export function getWorkspaceById(id: string) {
  return WORKSPACE_REGISTRY.find(w => w.id === id);
}

export function getWorkspaceByRoute(route: string) {
  return WORKSPACE_REGISTRY.find(w => route.startsWith(w.route));
}
