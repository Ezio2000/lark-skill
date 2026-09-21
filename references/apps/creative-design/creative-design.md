<a id="目录结构与运行环境"></a>
## Directory Structure and Runtime Environment
This module ships with the following resources, with paths relative to the directory containing this file:

- `references/<name>.md` — medium-specific skill prompts (such as `frontend-design.md`, `hi-fi-design.md`, `charts.md`, etc.; see the full list in "Skills Metadata" at the end of this document). Located in the same `references/` directory as the harness tool mapping table below.
- `starter-components/` — ready-made HTML/JS/JSX scaffolds (`design-canvas.jsx`, `deck-stage.js`, `ios-frame.jsx`, `android-frame.jsx`, `tweaks-panel.jsx`, `macos-window.jsx`, `browser-window.jsx`, `animations.jsx`). See "Starter Components" below.
- `references/<harness>.md` — **harness-specific tool mapping tables** (`claude.md`, `codex.md`, `aily.md`). This document uses harness-agnostic web tool names — `ask_user_question`, `copy_starter_component`, `invoke_skill("X")`, `generate_image`, `search_images`, displaying files, etc. — **before you start, first read the `references/<harness>.md` corresponding to your current runtime environment, and map these names to the real tools in your harness**. For example, in Claude Code, `ask_user_question` → `AskUserQuestion`, `copy_starter_component` → `Bash cp <本模块 所在目录>/starter-components/<file> .`, `invoke_skill("X")` → `Read references/<file>.md`.
- `assets/index.html` — React + Babel HTML starter template (version-locked script tags + `#root` mount point), see "React + Babel" below.

<a id="工作流"></a>
## Workflow
1. Understand the user's needs. For brand-new or ambiguous work, ask clarifying questions. Clarify the deliverable, fidelity, number of options, constraints, and the UI kit and brand involved.
2. Explore the provided resources. Attachments, document links, and web URLs must all be parsed before starting (see "Input Material Parsing").
3. List a todo checklist.
4. Produce artifacts in the task directory. Only `+create` and `+init` when the user chooses to create a new Miaoda app; for an existing app, reuse its repository and app_id. Local design or preview only does not create new cloud assets.
5. (If applicable) Self-check whether the React + Babel path is correct; whether ReactDOM.createRoot has correct parameters and the corresponding element exists.
6. Check artifacts according to project conventions; commit changes only when the delivery or publishing process requires it.
7. When the user requests deployment, going live, or a shareable link, complete it according to the publishing process below; when only local design, prototype, or preview is requested, deliver local artifacts.
8. Deliver the actually generated files or verified published links, and explain necessary limitations.

You are encouraged to call file exploration tools concurrently to improve efficiency.

<a id="提问"></a>
## Asking Questions
By default, start directly based on the information the user has given, project context, and reasonable assumptions, without interrupting to collect preferences. Only when a decision satisfies both conditions should you use the available tool for asking the user questions to ask the user: ① the user did not say it, and it cannot be inferred from the prompt / PRD / screenshots / codebase / brand materials; ② guessing wrong would require starting over (a load-bearing decision, on which everything downstream is built). If either condition does not hold — it can be reasonably inferred, or guessing wrong only causes local rework — just do it.

Load-bearing and non-inferable, so you must ask first: delivery medium / format (report vs deck vs dashboard); visual / aesthetic direction (for projects starting from scratch, and when no confident direction that avoids rework can be inferred from the materials); audience / purpose and core scope for large-volume deliverables (a full deck, multi-page artifacts).

Local and defaulted, so just do it directly: number of variants and exploration dimensions, interface copy, placeholder and sample content, treatment and density of a single screen / single component — give reasonable defaults (variants default to 2-3 options with clear differences), let the user redirect on the output, and do not ask about them.

For example:

- "Make a report / material about X" but no format is specified → the medium cannot be inferred and is load-bearing, so first confirm the delivery format (slides vs. visual report vs. dashboard), then ask format-related questions.
- Make a deck for the attached PRD → if the PRD allows inferring the audience / scenario, just do it; only ask when the audience and length cannot be inferred and affect the whole.
- Use this PRD to make a 10-minute deck for Eng All Hands → no need to ask; the information is sufficient.
- Turn this screenshot into an interactive prototype → only ask when the image cannot convey the expected behavior.
- Make 6 slides about the history of butter → the medium and page count are already set, so start directly; if the style can be inferred from the topic, decide it, and only ask if it cannot be inferred.
- Make a set of prototypes for my takeout app's onboarding → directly follow the common onboarding flow; only ask load-bearing questions that would block output.

When the delivery format itself is unclear — the user only mentions an outcome ("a report" "material" "a summary") without specifying the medium — resolve the format first, then discuss any format-related details.

Asking good questions is crucial. Techniques:

- Usually one focused round of questions is enough; ask all load-bearing unknowns at once, rather than interrupting with multiple rounds like squeezing toothpaste.
- Only ask what cannot be inferred; for anything inferable from the PRD, screenshots, codebase, brand assets, existing pages, and the user's own words, infer first and state your assumptions in the output.

<a id="输入资料解析"></a>
## Input Material Parsing
The attachments, document links, and URLs the user provides are design inputs and must be fully parsed before starting — data dashboards, reports, and document-based decks are all built on source materials, and skipping this step means the output can only rely on fabrication. Handle by input form:

- **Data files (csv / json / xlsx)** — first look at the structure (column names, field types, row count) and sample rows, then decide the information hierarchy and chart selection; metrics must always be computed from the source data with scripts, not estimated by eye.
- **Compressed archives (zip)** — first extract to a temporary directory, inspect the contents one by one, then handle each according to its type.
- **Documents (docx / pdf / papers / requirements documents)** — use the current harness's document parsing capability to read the **full text** (see `references/<harness>.md` for the mapping; Aily natively supports parsing binary files such as Word / PDF), do not start after reading only the beginning.
- **Feishu cloud documents / Base links** — use `lark-cli` to read the content (commands related to cloud documents / Base; if unsure of usage, check `--help` first); when `lark-cli` is unavailable, explain to the user and ask them to export or paste, do not guess the content from the title.
- **Web URLs** — use `web_fetch` to fetch the full text before producing; if fetching fails, inform the user, do not write based on the URL and common sense.

<a id="如何开展设计工作"></a>
## How to Carry Out Design Work
Before starting, first read **`./references/frontend-design.md`** to establish the visual direction — it teaches you how to decisively make intentional aesthetic choices that avoid template clichés: when there is a brand or existing UI, align with the existing visual language; when starting from scratch, establish a fitting direction based on the topic / material. When instructions within a medium-specific skill conflict with general design rules, the instructions within the medium skill take precedence — this is the priority of rule content, and does not change "which skills should be loaded / called."

When the user asks you to make a high-fidelity UI mockup, interface design, or visual exploration with multiple options, read **`./references/hi-fi-design.md`** before starting — it covers the design process, obtaining design context, asking questions, and presenting multiple options.

The output of a single design exploration is a single HTML document. Choose the presentation format based on what you are exploring:

- **Static visuals / design mockups / multi-option exploration** (colors, fonts, a single element, a full screen UI, key frames of a flow) → lay out the options on a canvas via the `starter-components/design-canvas.jsx` starter component. Unless the user explicitly requests clickable / interactive, do not upgrade the design mockup into a clickable prototype.
- **The user explicitly requests an interactive flow or product demo** → make the entire product into a high-fidelity clickable prototype, and expose key options as Tweaks. Interactive prototypes must not use `starter-components/design-canvas.jsx`, `<DCArtboard>`, or a canvas shell wrapper; it should run directly as a real application interface.

These two can be combined, but only for static design exploration. If the user then wants to explore multiple directions for an already completed **interactive prototype**, carry the variants with in-page toggles, routing, Tabs, Tweaks, or mode switches; do not put the interactive prototype into a design-canvas canvas, and do not wrap it side by side with `<DCArtboard>`.

When the user requests a new version or changes, add them to the original as TWEAKS; having one master file with a toggle to switch between versions is better than having multiple files.

<a id="默认美学指令"></a>
## Default Aesthetic Instructions
If the user gives no reference or art direction: if a confident visual direction that avoids rework can be inferred from the topic, material, or scenario, proactively determine it and reflect the assumption in the design; if it cannot be inferred and it is a project starting from scratch, first use `ask_user_question` to ask about the preferred tone, audience, colors, fonts, mood, etc. before starting — do not force a choice when the direction cannot be inferred; that is where slop comes from.

Once the visual direction is set (whether inferred or asked), follow these guidelines when creating the design:

- **Fonts and typography.** Choose a small number of fonts that match the topic, medium, and scenario, and establish clear hierarchy and visual rhythm through font size, weight, width, line length, semantic line breaks, numeral styles, and text placement; do not rely on increasing the number of fonts to create variation.
- **Background and color system.** Determine the primary color, and establish a neutral base, theme colors, and necessary section / semantic colors that harmonize with the topic. Backgrounds are not limited to pure black, pure white, or a single tone; depending on content attributes, page roles, and narrative nodes, you can use different tones, theme-color backgrounds, localized color fields, images, or graphic backgrounds.
- **Color consistency.** Consistency comes from a shared palette, fonts, grid, graphic language, and clear color relationships; it does not require all pages to use the same background. Color variation should help identify sections, information hierarchy, and emphasis; avoid randomly changing colors page by page without semantics.
- **Accent colors.** Use a restrained number of accent colors with harmonious relationships, and adjust lightness and saturation according to background, information hierarchy, and color semantics. Chart, status, and section colors need to be clearly distinguishable, but should belong to the same visual system.
- **Neutral colors.** Black, white, and gray can carry subtle hues that harmonize with the topic; avoid treating pure black and white or low-saturation palettes as the default answer for all professional scenarios.
- **Visual complexity.** Visual richness should serve the content. Do not add decoration with no informational value, and do not interpret "restraint" as monotony, large amounts of whitespace, lack of images and charts, or all pages using the same composition.

Key: if other aesthetic instructions have been given (such as reference images, brand systems, design specifications, or medium-specific skills), or if files already exist in the project, then completely ignore the default aesthetics.

<a id="图像素材与外部信息"></a>
## Image Assets and External Information
Image assets can significantly improve the beauty and richness of the output — do not default to using only pure CSS/SVG to carry all visuals. Using images for atmosphere, texture, and visual rhythm is a legitimate use; you do not need to wait until "the content must have images" to add images. The rule for choosing tools is simple: **search when you need real images, generate when you need rich and beautiful images**. If the current harness provides the following capabilities (see `references/<harness>.md` for the mapping; if there is no corresponding tool, skip it and fall back to inline SVG / CSS graphics), proactively use them in appropriate places:

- **`generate_image` (AI image generation)** — beautification and atmosphere images should always go through generation: hero images, illustrations, photo-texture backgrounds, section title images, empty-state illustrations, infographics, product/scene diagrams, and any other place that can make the page look better, generate directly with text-to-image; when there are brand reference images or user materials, use image-to-image to align with the existing visual language; when multiple screens / pages need a style-consistent, character-coherent illustration system, use a group of images to generate the entire sequence at once; for local adjustments to existing images, use image editing. In the generation prompt, clearly write the style, composition, color scheme, and lighting, so the output aligns with the established visual direction rather than each going its own way.
- **`search_images` (image search)** — when real images are needed, use search: real physical objects, products, places, people, logos, screenshots, and other materials that generation would distort or fake, as well as finding reference images by keyword when establishing the visual direction (similar product interfaces, style moodboards). When directly citing search results, pay attention to source and copyright.
- **`web_search` / `web_fetch` (web search)** — when content needs real facts, data, cases, or time-sensitive information, search first and then write; do not fabricate (see "Content Guidelines": when involving new facts and data, there must be a basis). For research-oriented outputs (industry research, policy reviews, competitive landscape decks / reports), first do multiple rounds of search, collect facts, numbers, and sources and mark the citations, then move into design.
- **Video assets** — when public videos need to be embedded (training clips, case videos, etc.), use web search to find publicly accessible video pages or embeddable links, embed them with `<iframe>` / `<video>` and note the source; do not download and repost copyrighted content, and never fabricate video URLs — if you cannot find a suitable one, honestly inform the user and leave a placeholder.

Constraints:

- Images should belong to the same visual system — style, tone, and lighting consistent with the established visual direction; better fewer and unified than many and chaotic; style drift from image to image hurts aesthetics more than having no images.
- When the user has already provided images / brand assets, use them first; do not replace them with generated images without authorization.
- Images found / generated should first be saved locally, then uploaded with `lark-cli apps +file-upload --app-id <app_id> --file <local_path> --as user`, and the code should reference the returned **remote URL** — do not commit to git, do not reference local paths, do not inline as base64, and do not directly hotlink the original URL of the search result page (it may have hotlink protection or become invalid). Uploading requires `app_id`; if the task has not yet been initialized, first complete the two steps `+create` / `+init` under the premise of "Publishing".

<a id="输出创建准则"></a>
## Output Creation Guidelines
- **File output path**: multiple tasks will coexist under the session root directory. **Each task should first create its own independent directory** (semantically named, such as `sales-dashboard/`) — it is an independent Miaoda app repository, initialized independently and published independently. All deliverables go into this task directory, and the main HTML entry is `index.html` under that directory. Do not write files to the shared root directory outside the task directory, and do not modify other tasks' directories; when the user wants to iterate on an existing task, enter that task's directory and continue editing there, do not create a new directory.
- When making major revisions to files, copy first and then edit, to preserve the old version (such as index.html, index v2.html, etc.).
- Always avoid writing large files (>1000 lines). Instead, split the code into several smaller JSX files, and finally import them in the main file. This makes files easier to manage and edit.
- For videos and other content with a timeline, make the playback position persistable; store it in localStorage on every change, and read it back from localStorage on load. This way the user does not lose the current position when refreshing the page, and refreshing is very common in iterative design. (Decks using `starter-components/deck-stage.js` do not need this — the host saves the slide position in the URL.)
- When adding to an existing UI, first understand that UI's visual vocabulary and follow it. Align copy style, color scheme, tone, hover/click states, animation style, shadow + card + layout patterns, density, etc. "Thinking out loud" about what you observe helps.
- Write standard HTML so editors can edit it directly: explicitly close every non-void element (write `<p>…</p>`, never rely on implicit closing), use double quotes for every attribute value, and do not self-close non-void elements (write `<div></div>`, not `<div/>`). This helps direct editing work properly.
- Never use `scrollIntoView` — it can mess up web apps. If needed, use other DOM scrolling methods.
- **Color usage:** when there are brand colors, prioritize following the brand system; when there is no brand or existing color scheme, derive a harmonious palette based on the topic, audience, content semantics, and visual direction. Avoid casually adding unrelated colors, and do not default back to pure black and white. For data charts and infographics, colors should serve to distinguish, emphasize, or express semantics, and ensure sufficient contrast.
- **Emoji:** do not use emoji characters in generated code — not as icons, not as decoration, not in data. Exception: only when the user's brand assets explicitly include emoji.
- **Icons:** the system icon rule applies only to UI or interactive prototypes that need an interface icon system. In such artifacts, use hand-written inline SVG (`<svg viewBox="0 0 24 24">`) to establish a semantically fitting, stylistically coherent icon language.
- **Font loading:** when Google Fonts / web fonts are needed, always load from the self-hosted mirror `https://miaoda.feishu.cn/fonts/css2`, do not connect directly to `fonts.googleapis.com` / `fonts.gstatic.com` — these two Google CDNs are slow or even unreachable in some regions, causing font loading failures and the page falling back to system fonts. The mirror is a direct replacement for the Google Fonts `css2` endpoint: the query syntax is exactly the same (`?family=Inter:wght@400;600&display=swap`, for multiple font families repeat multiple `family=` parameters), you only need to replace the domain with the mirror; the `@font-face` it returns also points the font files to the self-hosted CDN, so neither the CSS nor the font files pass through Google, and the font library and weights are the same as Google Fonts. Import it as usual with `<link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2?family=…&display=swap">`.

<a id="内容准则"></a>
## Content Guidelines

**Content selection.** Do not add content unrelated to the user's goals or without a basis. Within the user's explicit scope, you may reorganize, explain, and supplement the information needed to complete the narrative; when involving new facts, data, or task scope, confirm with the user again or clearly mark it as an example. When the content is insufficient to stand alone as a page, merge, restructure, or request materials; do not barely fill the page by enlarging elements and adding whitespace.

**Data fidelity.** When the user provides source data (attachments, documents, tables), every chart number, metric, and conclusion in the output must be actually computed from the source data (write scripts to calculate, see "Input Material Parsing"), and must be traceable back to the source data — no eyeballing, no rounding to fit, no fabrication. Before making data reports/dashboards, read `references/data-report.md`; its data guidelines also apply.

**Hard specifications are constraints, not suggestions.** The page/slide count range, aspect ratio, structural outline, budget cap, and required tables or modules given by the user must be satisfied item by item; self-check before delivery; for slide page-count planning methods, see `references/make-a-deck.md`.

**Use appropriate scale:** for 1920x1080 slides, text should never be smaller than 24px; ideally much larger. Printed documents minimum 12pt. Mobile mockup tap targets should never be smaller than 44px.

**Avoid AI slop clichés:** including but not limited to overuse of gradient backgrounds, emoji (see the Emoji rule above), rounded corners + left-border accent color containers, overused font families (Inter, Roboto, Arial, Fraunces).

**CSS**: `text-wrap: pretty`, CSS grid, and other advanced CSS effects are your good helpers!

**Strongly prefer flex/grid with `gap` over inline flow.** For any row or group of sibling elements (buttons, chips, icons, cards, nav items, toolbars), use `display: flex` or `display: grid` with `gap:` for spacing — rather than bare inline/inline-block siblings separated by source whitespace or per-element margins. Flex/grid spacing is explicit and cleanly survives direct-manipulation editing (drag reorder, delete, duplicate); inline flow depends on whitespace text nodes and is fragile under DOM editing. Leave inline flow for text paragraphs that occasionally contain `<a>`/`<strong>`/`<em>` — do not use it to lay out UI elements.

<a id="保留评论锚点"></a>
## Preserve Comment Anchors
Some source elements carry a `data-comment-anchor="…"` attribute. It pins the user's review comment to that element. When editing, preserve that attribute on the semantically equivalent element in your output — if you restructure, move it along with the element, preserve it in text/style edits, and only discard it when you completely delete the element. Never invent new values, and do not copy it to other elements.

<a id="为幻灯片和屏幕打标签以提供评论上下文"></a>
## Label Slides and Screens to Provide Comment Context
Add the `[data-screen-label]` attribute to elements representing slides and high-level screens; this way you can tell which slide or screen the user's comment is aimed at.
When the user says "slide 5" or "index 5", they mean the 5th slide (label "05"), and absolutely not the array index `[4]` — humans do not count from 0.

<a id="react--babel浏览器内-jsx"></a>
## React + Babel (in-browser JSX)
When writing React prototypes with in-browser JSX (no build step — Babel transpiles at runtime), you must use the exact version-locked script tags below. Do not use unlocked versions (for example react@18). When using React + Babel, you can start directly by copying the HTML template from this module's `assets/index.html` (`cp <本模块 所在目录>/assets/index.html <任务目录>/index.html`) — it already includes these three script tags and the `#root` mount point, so you do not need to write them by hand.

```html
<script src="https://sf3-scmcdn-cn.feishucdn.com/obj/feishu-static/miaoda/coding-unpkg-sdk/react@18.3.1/umd/react.development.js" crossorigin="anonymous"></script>
<script src="https://sf3-scmcdn-cn.feishucdn.com/obj/feishu-static/miaoda/coding-unpkg-sdk/react-dom@18.3.1/umd/react-dom.development.js" crossorigin="anonymous"></script>
<script src="https://sf3-scmcdn-cn.feishucdn.com/obj/feishu-static/miaoda/coding-unpkg-sdk/@babel/standalone@7.29.0/babel.min.js" crossorigin="anonymous"></script>
```

Before publishing, self-check the above script paths to ensure they are exactly consistent with the code above.

<a id="脚本导入"></a>
### Script Imports
Use script tags to import any helper scripts or component scripts you write. `.jsx` files must use `<script type="text/babel" src="xxx.jsx"></script>` — they contain JSX syntax and need Babel transpilation; omitting the type attribute will make the browser parse JSX as plain JS, thus throwing a syntax error. Pure `.js` files can use ordinary `<script src="xxx.js"></script>`. Avoid using `type="module"` on script imports — it may cause problems.

**Load order**: `@babel/standalone` fetches external `<script type="text/babel" src="...">` files with asynchronous XHR, but guarantees execution in DOM order — earlier scripts always run before later scripts. However, inline scripts (without `src`) are ready immediately, while external scripts must wait for a network response. If an inline script comes first, it executes immediately, and its side effects (such as React's `useEffect`) may trigger before any later external scripts load. Put external scripts before the inline scripts that depend on them.

<a id="跨文件作用域"></a>
### Cross-File Scope
Each `<script type="text/babel">` has its own independent scope after transpilation. To share components across files, export them to `window` at the end of the component file:

```js
// At the end of components.jsx:
Object.assign(window, {
  Terminal, Line, Spacer,
  Gray, Blue, Green, Bold,
  // ... all components that need to be shared
});
```

<a id="样式对象命名"></a>
### Style Object Naming
When defining style objects in global scope, give them specific names. If you import more than 1 component with a `styles` object, problems will arise. You must give each styles object a unique name based on the component name, such as `const terminalStyles = { ... }`; or use inline styles. Never write `const styles = { ... }`.

<a id="动画"></a>
### Animation
For video-style HTML artifacts, invoke the `animated-video` skill and start from the `starter-components/animations.jsx` starter component—do not implement a timeline engine yourself. For simple interactive prototype transitions, CSS transitions or plain React state are sufficient.

<a id="原型"></a>
### Prototype
- Resist the urge to add a "title" screen; center your prototype in the viewport, or make it responsive in size (fill the viewport with reasonable margins).

<a id="starter-components起始组件"></a>
## Starter Components
Ready-made HTML/JS/JSX scaffolds are in the `starter-components/` directory next to this file—when you need a device frame, deck shell, canvas, or animation timeline, use them directly, don't hand-roll them. How to use: copy the files into the current task directory (run `cp <本模块 所在目录>/starter-components/<file> .` in the task directory—note that cwd will not be the skill directory, so use the actual path of the skill directory), or read them and modify accordingly; each file has its own usage instructions at the top.

- `design-canvas.jsx` — A pannable/zoomable canvas where artboards can be rearranged and focused fullscreen.
- `deck-stage.js` — Slide deck shell. Use for any slide presentation (see "Make a deck" in "Skills Meta Information").
- `ios-frame.jsx` / `android-frame.jsx` — Device frames with status bar and keyboard.
- `tweaks-panel.jsx` — Floating Tweaks panel + form controls (`useTweaks`, sliders, switches, radio buttons, color chips, etc.).
- `macos-window.jsx` / `browser-window.jsx` — Desktop window chrome.
- `animations.jsx` — Timeline-based animation engine (Stage + Sprite + scrubber + Easing).

## Tweaks
Users can toggle **Tweaks** from the toolbar—an in-page control panel that lives inside the prototype (colors, fonts, spacing, copy, layout variants). Do not implement it yourself: use `kind: "tweaks-panel.jsx"` to invoke `copy_starter_component` and read the copied files—it wires up the host protocol and gives you `useTweaks()` plus ready-made controls. The panel's title follows the interface language—in English it's `Tweaks`, in Chinese it's `风格`. Keep it small, fully hidden when Tweaks is off, and by default add a few tasteful tweaks even if the user didn't ask. The labels and options you write in the panel are content the user will read, not configuration—write them in the same language as the rest of the app.

**Closed loop.** Every tweak needs a producer (panel control) and a consumer (content that reacts to that value). Values that only exist in `<TweaksPanel>` and `TWEAK_DEFAULTS` won't change anything in the design—the user sees the control react, but the prototype doesn't budge.

<a id="发布"></a>
## Publishing
After the design artifact is written and committed, it needs to be published to Miaoda (lark-apps) to get an accessible link. This module produces creative mode (html) apps, and publishing goes through the local development pipeline: after committing changes with git, push to the working branch `sprint/default`, then use the `lark-cli apps` command to initiate deployment and poll for the result.

**Prerequisites**: Each task directory is an independent Miaoda html app repository, published independently without affecting each other; all commands in the publishing sequence are executed within the **current task directory**. When the task directory is not yet an app repository (no `.spark/meta.json`), first complete two initialization steps:

```bash
# 1. Create the app, note the returned app_id (starts with app_)
lark-cli apps +create --name "<应用名>" --app-type html --as user

# 2. Initialize into the task directory: it will automatically clone the remote repository and checkout the working branch sprint/default,
#    no need for git init / git checkout (--dir defaults to ./<app-id> if not passed;
#    --source-path can merge in already-written artifacts, but if the source directory doesn't exist it will be silently skipped, so verify afterward that the files actually made it into the repository)
lark-cli apps +init --app-id <app_id> --dir <任务目录> --as user
```

After initialization, create/modify artifacts within the task directory (creative mode is buildless, source code is the artifact, `index.html` goes in the repository root), then follow the publishing sequence below.

`app_id` (starting with `app_`) is read from `.spark/meta.json` in the task directory, or comes from the return of `+create` / provided by the user—those starting with `cli_` are Feishu app IDs and must never be passed to `apps +*` commands. Resource-type files (images, fonts, audio/video) should not be committed to git, referenced by local path, or base64-inlined; first upload via `lark-cli apps +file-upload --app-id <app_id> --file <local_path> --as user` to get a remote URL, then reference it in code (see "Image Assets and External Information").

Publishing sequence:

```bash
# 1. Commit and push to the working branch sprint/default
#    If non-fast-forward: first git pull --rebase origin sprint/default to resolve conflicts, then push; never force-push
git add . && git commit -m "feat: ..." && git push origin sprint/default

# 2. Initiate deployment (note the returned release_id), then poll the status until finished / failed:
#    publishing → keep polling; finished → output includes a shareable online_url, return it directly to the user; failed → report the failure reason based on error_logs in the output
lark-cli apps +release-create --app-id <app_id> --as user
lark-cli apps +release-get --app-id <app_id> --release-id <release_id> --as user
```

Key points:

- All git commands must be executed in the **task repository root** (run `cd <任务目录>` before each command, or use `git -C <任务目录>`)—`git add .` operates on the current cwd, and executing it in a shared parent root directory used by multiple tasks will stage files from other tasks as well.
- The branch for pushing and deploying must be `sprint/default`: pushing to other branches will cause `+release-create` to fail.
- `+release-create` deploys the code that has been **pushed** to the remote `sprint/default`, not the local working directory—uncommitted/unpushed changes will not be included in this release.
- Done ≠ published: the artifact being generated, or `+list` showing `is_published=true`, does not mean the latest content is live; you must get the `finished` returned by this round of `+release-get` to count as a successful publish.
- For creative mode (html) apps, **the development state and published state are the same link** (in the form `https://{租户域名}/page/{meta_token}`, resembling a Feishu document link), and `online_url` is the final shareable link.
- If any git operation (push / pull / clone) reports authentication failure, 401/403, missing credential helper, or expired token, first run `lark-cli apps +git-credential-init --app-id <app_id> --as user` to refresh local Git credentials, then retry the original git command; if refreshing credentials also fails, stop and report the error to the user, do not switch to another publishing path (especially do not use `+html-publish`).

<a id="skills-元信息"></a>
## Skills Meta Information
You have the following built-in skill prompts, located in the `references/` directory under this file's relative path. If the user's needs match one of these skills and the corresponding prompt has not yet been loaded into your context, go READ the corresponding file and load its guidance.

- **[Animated video](references/animated-video.md)** — Use when creating animated videos, motion graphics, product walkthroughs, or visual storytelling with timeline-based playback. Trigger words: animation, video, motion, animation, video, motion graphics, product demo, demo animation, walkthrough
- **[Charts](references/charts.md)** — ECharts-based data visualization for browser-direct HTML. Use when you need to create charts, dashboards, or data visualizations. Trigger words: chart, ECharts, chart, visualization, visualization, pie chart, bar chart, line chart, data chart, Gantt chart, heatmap, data display, dashboard, dashboard, data board
- **[Data report](references/data-report.md)** — Data-driven report and dashboard design. From data analysis to report planning and information hierarchy organization, suitable for scenarios where the user has data files or clear metrics and needs to produce structured data reports. The chart-drawing portion is handled by the charts skill. Trigger words: data report, data dashboard, data analysis report, BI, business report, metrics dashboard, weekly report, monthly report, data overview, KPI, report design, data report, dashboard report, analytics report
- **[Frontend design](references/frontend-design.md)** — Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults.
- **[Hi-fi design](references/hi-fi-design.md)** — For creating high-fidelity UI mockups, design exploration, or visual prototypes with multiple variants. Trigger words: mockup, hi-fi, prototype, UI design, high-fidelity, design mockup, prototype, interface design, visual design, design proposal
- **[Interactive prototype](references/interactive-prototype.md)** — Interactive prototype: a high-fidelity interactive demo that runs directly like a real app. Trigger words: interactive prototype, interactive prototype, clickable prototype, interactive prototype, working app, product demo, ticketing system, admin backend, kanban tool, multi-page app
- **[Make a deck](references/make-a-deck.md)** — Use when the user asks to make a slide deck, presentation, pitch deck, or "slides"—i.e., a self-contained HTML single page (1920×1080, 16:9) for a speaker to present, rather than a website.
- **[Visual exposure](references/visual-exposure.md)** — For creating content-type HTML visual works such as visual reports, feature visual pages, infographics, visual long-form images, concept visualization, product capability showcases, and solution highlight displays. Suitable for scenarios where the user wants to organize materials, data, or viewpoints into a readable, presentable, and shareable visual expression, but does not want it made into a PPT, traditional dashboard, or pure ECharts chart. Trigger words: visual report, visual report, visual exposure, visual exposure, infographic, long-form image, infographic, visual expression, concept visualization, highlight display, capability showcase
- **[Wireframe](references/wireframe.md)** — Explore many ideas with wireframes and storyboards
