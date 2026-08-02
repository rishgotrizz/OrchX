import { create } from "zustand";

interface UiState {
  isInspectorOpen: boolean;
  toggleInspector: () => void;
  activeWorkspace: string;
  setActiveWorkspace: (workspace: string) => void;
}

export const useUiStore = create<UiState>((set) => ({
  isInspectorOpen: false,
  toggleInspector: () => set((state) => ({ isInspectorOpen: !state.isInspectorOpen })),
  activeWorkspace: "mission-control",
  setActiveWorkspace: (workspace) => set({ activeWorkspace: workspace }),
}));
