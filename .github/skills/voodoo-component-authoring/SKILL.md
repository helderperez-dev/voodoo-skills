---
name: voodoo-component-authoring
description: Author Voodoo UI components with semantic HTML, session-safe events, theme tokens, responsive behavior, accessibility states, and executable examples.
---

# Voodoo Component Authoring

Start with the stable component rubric and reuse the preferred family API
before introducing a new component. Keep rendering declarative and let the
Runtime own event/session authority.

## Component contract

- Use semantic elements and explicit labels, names, roles, and button types.
- Cover loading, empty, error, disabled, read-only, overflow, and long-content
  states where the component can enter them.
- Consume semantic theme tokens; do not embed raw colors or inline scripts.
- Keep event bindings scoped to the current UI session and avoid global
  browser broadcasts.
- Add a focused semantic test, keyboard/browser coverage, and one realistic
  composition example before promoting maturity.

Run the component maturity, style-token, accessibility, and browser contracts
before changing a stable component's public API.
