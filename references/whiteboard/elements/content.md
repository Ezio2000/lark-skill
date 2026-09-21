<a id="内容规划"></a>
# Content Planning

Core principle: **The amount of information should match the level of detail the user needs.** If the user says "draw a simple architecture diagram," draw a simple one; only when they say "draw a complete microservices architecture" should you draw a complex one. Do not take it upon yourself to **over-expand**.

**When the user's prompt is short/vague** (such as "draw a funnel chart" or "draw an architecture diagram"), do not just output the literal content. You should appropriately supplement reasonable content for that domain.

<a id="信息量参考"></a>
## Information Volume Reference

| User Requirement | Reasonable Information Volume |
|---------|------------|
| "Draw a simple XX architecture diagram" | 3 layers, 2-3 nodes per layer, no sidebar |
| "Draw an XX architecture diagram" (ordinary request) | 3-4 layers, 3-4 nodes per layer |
| "Draw a complete/detailed XX architecture diagram" | 4-5 layers, 4-6 nodes per layer, sidebar allowed (sidebar at most 2-3 items) |
| Flowchart | 6-10 steps + 1-2 conditional branches |
| Comparison table | 4-6 dimensions, 1-2 lines of explanation per cell |
| Organizational structure | 3-4 layers, 2-4 child nodes under each parent node |

**Node text**: title + brief description (such as "User Service\nRegistration, login, and permission management"), do not write long paragraphs. Descriptions of 12 characters or fewer are best.

<a id="分组"></a>
## Grouping

Each group has 2-5 nodes. If more than 5, split into subgroups.

<a id="连线预判"></a>
## Connection Pre-estimation

| Number of Connections | Strategy |
|--------|------|
| ≤8 | Draw one by one |
| 9-15 | Representative connections |
| >15 | Layer to layer, or fall back to simplification |

<a id="精简触发条件"></a>
## Simplification Trigger Conditions

Only simplify when the layout cannot fit:

| Problem | Simplification Method |
|------|---------|
| Node text does not fit | Shorten the description text |
| More than 5 nodes in one row | Split into two rows or merge similar ones |
| Crossing connections | Reduce the number of connections |
