import { registerRenderer } from "@/lib/renderer-registry";
import { MarkdownPreviewDriver } from "./MarkdownPreviewDriver";
import { HtmlPreviewDriver } from "./HtmlPreviewDriver";
import { CodePreviewDriver } from "./CodePreviewDriver";
import { JsonPreviewDriver } from "./JsonPreviewDriver";

export function initializePreviewDrivers() {
  registerRenderer({
    id: "driver-markdown",
    name: "Markdown Renderer",
    supportedMimeTypes: ["text/markdown"],
    component: MarkdownPreviewDriver
  });
  
  registerRenderer({
    id: "driver-html",
    name: "HTML Renderer",
    supportedMimeTypes: ["text/html"],
    component: HtmlPreviewDriver
  });

  registerRenderer({
    id: "driver-json",
    name: "JSON Renderer",
    supportedMimeTypes: ["application/json"],
    component: JsonPreviewDriver
  });

  registerRenderer({
    id: "driver-typescript",
    name: "TypeScript Renderer",
    supportedMimeTypes: ["text/typescript"],
    component: CodePreviewDriver
  });
}
