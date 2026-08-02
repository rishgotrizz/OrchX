import { registerWidget } from "@/lib/widget-registry";
import { FileSearch, Layers, Info, Search, Sparkles, LayoutPanelTop, Network } from "lucide-react";
import { DocumentExplorerWidget } from "./DocumentExplorerWidget";
import { DocumentEditorWidget } from "./DocumentEditorWidget";
import { DocumentInspectorWidget } from "./DocumentInspectorWidget";
import { GlobalSearchWidget } from "./GlobalSearchWidget";
import { DocumentToolbarWidget } from "./DocumentToolbarWidget";
import { AISuggestionsWidget } from "./AISuggestionsWidget";
import { KnowledgeGraphWidget } from "./KnowledgeGraphWidget";

const DEFAULT_MANIFEST = {
  version: "1.0.0",
  author: "OrchX Core",
  capabilities: ["read", "write"],
  permissions: ["documents"],
  refreshPolicy: "event" as const,
  category: "documents",
};

export function initializeDocumentWidgets() {
  registerWidget({ ...DEFAULT_MANIFEST, id: "doc-explorer", title: "Explorer", description: "File tree", icon: FileSearch, defaultSize: 40, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: DocumentExplorerWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "doc-editor", title: "Editor", description: "Multi-tab editor", icon: Layers, defaultSize: 60, minSize: 40, preferredLayout: "horizontal", priority: "high", supportedLayouts: ["all"], component: DocumentEditorWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "doc-inspector", title: "Inspector", description: "Metadata", icon: Info, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: DocumentInspectorWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "global-search", title: "Search", description: "Global search", icon: Search, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: GlobalSearchWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "doc-toolbar", title: "Toolbar", description: "Actions", icon: LayoutPanelTop, defaultSize: 10, minSize: 5, preferredLayout: "horizontal", priority: "high", supportedLayouts: ["all"], component: DocumentToolbarWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "ai-suggestions", title: "AI Suggestions", description: "Smart actions", icon: Sparkles, defaultSize: 20, minSize: 15, preferredLayout: "horizontal", priority: "medium", supportedLayouts: ["all"], component: AISuggestionsWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "knowledge-graph", title: "Knowledge Graph", description: "Relationships", icon: Network, defaultSize: 40, minSize: 30, preferredLayout: "grid", priority: "high", supportedLayouts: ["all"], component: KnowledgeGraphWidget });
}
