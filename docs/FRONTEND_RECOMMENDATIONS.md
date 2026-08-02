# Frontend Recommendations (Post-Freeze)

This document serves as a parking lot for feature concepts, UI ideas, and architectural recommendations discovered during the frontend stabilization sprints. Since the frontend is now permanently frozen, these ideas should only be considered for implementation if supported by future backend capabilities.

## Architecture Ideas
- **Unified Command Center**: Consider integrating the global search (`CommandPalette.tsx`) directly with backend AI orchestration to allow users to trigger complex workflows ("Deploy the e-commerce store") from anywhere.
- **Real-time Artifact Subscriptions**: Once the backend supports websockets, the artifact cards in the chat thread should stream their progress live rather than relying on optimistic mock delays.
- **Provider Registry UI**: Settings should dynamically pull supported models from the backend instead of hardcoding them, allowing users to effortlessly plug in their own custom fine-tunes.

## Interaction Polish
- **Voice Input Feedback**: When the microphone input is activated in the prompt bar, a subtle visualizer could respond to audio levels for better feedback.
- **Inline Editing of PRDs**: Allow users to click directly into a generated PRD in the Documents Studio to make manual edits before feeding it back into the AI context window.
