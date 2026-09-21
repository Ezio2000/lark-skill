Create a fully interactive prototype with realistic state management and transitions. Use React useState/useEffect for dynamic behavior. Include hover states, click interactions, form validation, animated transitions, and multi-step navigation flows. It should feel like a real working app, not a static mockup.

Do not wrap interactive prototypes in `design-canvas.jsx`, `<DCArtboard>`, or any pan/zoom artboard shell. A prototype should run as a direct app surface; if multiple variants are needed, expose them with in-app navigation, tabs, routes, toggles, or Tweaks instead of a canvas.

<a id="多页面与路由"></a>
## Multi-page and Routing

Build multi-page prototypes as a normal MPA: one HTML file per page, with the entry point fixed at the project root `index.html`, and navigation between pages via ordinary relative-path links (`<a href="detail.html">`). Do not introduce any router library—there is no router in the version-locked CDN list, and do not use `type="module"` to simulate SPA routing. Split shared components and styles into separate `.jsx` / `.css` files that each page imports individually; put state that must persist across pages (ticket lists, kanban data, etc.) in localStorage and read it back on load; pass parameters between pages via URL query.

<a id="像真实应用而不是摆拍"></a>
## Like a Real App, Not a Staged Mockup

- Prepare a set of mock data that feels close to the business (names, statuses, and timestamps should all look real), and render the page from that data—do not hard-code content in the markup.
- Every visible button, input, and toggle must respond: submissions have validation and feedback, lists can be added to, deleted from, and edited, states transition, and empty states are designed. A control that does nothing when clicked hurts credibility more than not having that control at all.
- Following [`../creative-design.md`](../creative-design.md) "Tweaks", expose key options (theme color, density, layout variants, etc.) with `tweaks-panel.jsx`; do not implement your own control panel.
