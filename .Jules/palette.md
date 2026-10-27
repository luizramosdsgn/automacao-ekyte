## 2025-05-18 - Accessibility and Focus Indicators for Eel Web UI
**Learning:** Eel-based static web components can lack standard form field associations and focus indicators when using custom dark theme styling.
**Action:** Always associate `<label for="...">` with inputs, provide `role="log"` and `aria-live="polite"` for real-time terminal output, maintain `aria-valuenow` on custom progress bars, and explicitly set `:focus-visible` ring outlines.
