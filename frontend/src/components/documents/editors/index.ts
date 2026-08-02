import { registerEditor } from "@/lib/editor-registry";
import { MarkdownDocumentDriver } from "./MarkdownDocumentDriver";
import { CodeDocumentDriver } from "./CodeDocumentDriver";

export function initializeDocumentEditors() {
  registerEditor({
    id: "editor-markdown",
    name: "Markdown Editor",
    supportedTypes: ["markdown"],
    component: MarkdownDocumentDriver
  });

  registerEditor({
    id: "editor-code",
    name: "Code Editor",
    supportedTypes: ["prompt", "workflow", "json", "yaml", "html", "react"],
    component: CodeDocumentDriver
  });
}
