import { registerWidget } from "@/lib/widget-registry";
import { Activity, Network, ListTodo, Zap, CreditCard, Lightbulb, Users, Cpu, History } from "lucide-react";
import { MissionFeedWidget } from "./MissionFeedWidget";
import { WorkflowOverviewWidget } from "./WorkflowOverviewWidget";
import { TaskTimelineWidget } from "./TaskTimelineWidget";
import { QuickActionsWidget } from "./QuickActionsWidget";
import { CreditsSummaryWidget } from "./CreditsSummaryWidget";
import { AiSuggestionsWidget } from "./AiSuggestionsWidget";
import { ActiveSessionsWidget } from "./ActiveSessionsWidget";
import { SystemHealthWidget } from "./SystemHealthWidget";
import { RecentActivityWidget } from "./RecentActivityWidget";

const DEFAULT_MANIFEST = {
  version: "1.0.0",
  author: "OrchX Core",
  capabilities: ["read"],
  permissions: ["mission-control"],
  refreshPolicy: "event" as const,
  category: "orchestration",
};

export function initializeWidgets() {
  registerWidget({ ...DEFAULT_MANIFEST, id: "mission-feed", title: "Mission Feed", description: "Live events", icon: Activity, defaultSize: 40, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: MissionFeedWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "workflow-overview", title: "Workflow Overview", description: "Workflow nodes", icon: Network, defaultSize: 30, minSize: 20, preferredLayout: "horizontal", priority: "high", supportedLayouts: ["all"], component: WorkflowOverviewWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "task-timeline", title: "Task Timeline", description: "Sequential steps", icon: ListTodo, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "high", supportedLayouts: ["all"], component: TaskTimelineWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "quick-actions", title: "Quick Actions", description: "Common actions", icon: Zap, defaultSize: 20, minSize: 15, preferredLayout: "grid", priority: "high", supportedLayouts: ["all"], component: QuickActionsWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "credits-summary", title: "Credits Summary", description: "Usage", icon: CreditCard, defaultSize: 20, minSize: 15, preferredLayout: "horizontal", priority: "medium", supportedLayouts: ["all"], component: CreditsSummaryWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "ai-suggestions", title: "AI Suggestions", description: "Recommendations", icon: Lightbulb, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "medium", supportedLayouts: ["all"], component: AiSuggestionsWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "active-sessions", title: "Active Sessions", description: "Running projects", icon: Users, defaultSize: 40, minSize: 20, preferredLayout: "vertical", priority: "medium", supportedLayouts: ["all"], component: ActiveSessionsWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "system-health", title: "System Health", description: "Kernel status", icon: Cpu, defaultSize: 40, minSize: 20, preferredLayout: "grid", priority: "high", supportedLayouts: ["all"], component: SystemHealthWidget });
  registerWidget({ ...DEFAULT_MANIFEST, id: "recent-activity", title: "Recent Activity", description: "Historical logs", icon: History, defaultSize: 30, minSize: 20, preferredLayout: "vertical", priority: "low", supportedLayouts: ["all"], component: RecentActivityWidget });
}
