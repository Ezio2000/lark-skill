<a id="iconpark-图标"></a>
# IconPark Icons

IconPark icons are written into slides XML via `<icon>`; `iconType` must come from this module's offline index to avoid assembling paths from memory.

<a id="机器优先流程"></a>
## Machine-First Workflow

```bash
uv run --project "<lark-root>" --locked python "<lark-root>/references/slides/scripts/iconpark_tool.py" search --query "增长趋势" --limit 8
uv run --project "<lark-root>" --locked python "<lark-root>/references/slides/scripts/iconpark_tool.py" resolve --name chart-line
uv run --project "<lark-root>" --locked python "<lark-root>/references/slides/scripts/iconpark_tool.py" list-categories
```

`search` returns a JSON array, each item containing `iconType`, `category`, `name`, `tags`, `score`. Directly write the selected `iconType` into the XML, and specify a visible color for the icon:

```xml
<icon iconType="iconpark/Charts/chart-line.svg" topLeftX="80" topLeftY="120" width="32" height="32">
  <fill>
    <fillColor color="rgba(37, 99, 235, 1)"/>
  </fill>
</icon>
```

<a id="使用规则"></a>
## Usage Rules

- Search first by default: semantic icon requirements must first use `iconpark_tool.py search --limit 8` or `--limit 10`, letting the agent make a second judgment from the candidates combined with layout semantics; do not read the full-text index, and do not fabricate non-existent `iconType`.
- Icons are used for concept hints, steps, statuses, metrics, roles, and navigation; do not fill the layout with irrelevant decorative icons.
- Common sizes: inline status icons 16-24px, card title icons 28-40px, hero visual icons 56-96px.
- Icons must be filled with color and have sufficient contrast with the background; for dark backgrounds, prefer placing them on a light-colored circular/square base, or use `rgba(255, 255, 255, 1)` as the icon fill color.
- When no suitable icon can be found, choose a substitute icon from the high-frequency examples (choose randomly, do not be monotonous), and do not leave empty icon slots.

<a id="高频示例"></a>
## High-Frequency Examples

| Semantics | iconType |
|---|---|
| Settings/Configuration | `iconpark/Base/setting.svg` |
| Goal | `iconpark/Base/aiming.svg` |
| Growth trend | `iconpark/Charts/positive-dynamics.svg` |
| Line trend | `iconpark/Charts/chart-line.svg` |
| Proportion | `iconpark/Charts/chart-proportion.svg` |
| Data dashboard | `iconpark/Charts/data-screen.svg` |
| Success | `iconpark/Character/check-one.svg` |
| Failure/Risk | `iconpark/Character/close-one.svg` |
| Team/User | `iconpark/Peoples/peoples.svg` |
| Security protection | `iconpark/Safe/protect.svg` |
| Global/Market | `iconpark/Travel/world.svg` |
| Email/Contact | `iconpark/Office/envelope-one.svg` |
