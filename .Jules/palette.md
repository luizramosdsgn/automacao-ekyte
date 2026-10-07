## 2026-03-30 - Form Controls and Progress ARIA Enhancements
**Learning:** Web interfaces utilizing dark theme inputs and custom progress bars often lack accessible label bindings and keyboard focus visibility, hindering screen readers and keyboard navigation.
**Action:** Always link form labels to inputs using `for` attributes, provide `aria-label` attributes on textareas and terminal logs, update `aria-valuenow` dynamically on progress bars, and supply clear `:focus-visible` styling for interactive controls.
