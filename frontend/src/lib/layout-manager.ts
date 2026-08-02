import { useLocalStorage } from "usehooks-ts";

export type LayoutPreset = "mission-control" | "preview-focus" | "document-review" | "runtime-monitor" | "default";

export function useLayoutManager(workspaceId: string, defaultPreset: LayoutPreset = "default") {
  const [activePreset, setActivePreset] = useLocalStorage<LayoutPreset>(
    `layout-preset-${workspaceId}`, 
    defaultPreset
  );

  return {
    activePreset,
    setActivePreset,
  };
}
