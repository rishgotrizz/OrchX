import { registerWidget } from "@/lib/widget-registry";
import { FileSearch, History, Info, TerminalSquare, BarChart2, LayoutPanelTop } from "lucide-react";
import { ArtifactExplorerWidget } from "./ArtifactExplorerWidget";
import { VersionHistoryWidget } from "./VersionHistoryWidget";
import { PropertiesInspectorWidget } from "./PropertiesInspectorWidget";
import { PreviewConsoleWidget } from "./PreviewConsoleWidget";
import { PreviewStatisticsWidget } from "./PreviewStatisticsWidget";
import { PreviewToolbarWidget } from "./PreviewToolbarWidget";

const DEFAULT_MANIFEST = {
  version: "1.0.0",
  author: "OrchX Core",
  capabilities: ["read"],
  permissions: ["preview"],
  refreshPolicy: "event" as const,
  category: "preview",
};

export function initializePreviewWidgets() {
  registerWidget({ ...DEFAULT_MANIFEST, id: "artifact-explorer", title: "Artifact Explorer", description: "File tree", icon: FileSearch, defaultSize: 40, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: ArtifactExplorerWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "version-history", title: "Version History", description: "Revisions", icon: History, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: VersionHistoryWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "properties-inspector", title: "Inspector", description: "Metadata viewer", icon: Info, defaultSize: 40, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: PropertiesInspectorWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "preview-console", title: "Console", description: "Logs", icon: TerminalSquare, defaultSize: 30, minSize: 20, preferredLayout: "horizontal", priority: "high", supportedLayouts: ["all"], component: PreviewConsoleWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "preview-statistics", title: "Statistics", description: "Metrics", icon: BarChart2, defaultSize: 30, minSize: 20, preferredLayout: "grid", priority: "medium", supportedLayouts: ["all"], component: PreviewStatisticsWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "preview-toolbar", title: "Toolbar", description: "Actions", icon: LayoutPanelTop, defaultSize: 10, minSize: 5, preferredLayout: "horizontal", priority: "high", supportedLayouts: ["all"], component: PreviewToolbarWidget });
}
