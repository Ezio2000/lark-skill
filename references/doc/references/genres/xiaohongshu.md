<a id="genre-contract-xiaohongshu-note--小红书笔记-platformxiaohongshu"></a>
# Genre Contract: Xiaohongshu Note (`platform.xiaohongshu`)

<a id="核心定位硬约束"></a>
## Core Positioning (Hard Constraints)

- The deliverable is a "Xiaohongshu-style" content draft in a Feishu document; it does not represent an actual post, nor does it execute Xiaohongshu platform review, prohibited-word, traffic, or commercial rules.
- The visual strategy defaults to `rich`, favoring a rich mix of images and text and a clear, relaxed reading experience, but decoration cannot replace content.
- The writing style is vivid, rhythmic, and image-rich, and may use emoji that fit the context.
- One note solves only one main problem; the title, cover, first screen, and body revolve around the same sense of gain and truly deliver it. Do not fabricate personal experiences, identities, numbers, effects, or user feedback; when material is insufficient, use second person, scenario-based explanation, or neutral narration.
- The Feishu source draft must not use `callout`; after generation, pass the `profile.blocks` check of the Draft Profile Check, and choose other blocks according to real information relationships.

<a id="适用与消歧"></a>
## Applicability and Disambiguation

Use this when the user explicitly asks for "Xiaohongshu note, Xiaohongshu writing method, Xiaohongshu style, red-book feel, XHS style"; where the content is stored does not affect whether this contract takes effect.

When Xiaohongshu is only used as a research object, data source, or business channel, this is not triggered: Xiaohongshu operation plans go to Workplace, platform data or competitor analysis goes to Report, and rule explanations go to Knowledge. If both a Xiaohongshu-style draft and a formal genre are requested, generate them separately and do not mix them.

<a id="笔记主任务"></a>
## Note Main Task

| Main Task | Content Spine |
|-|-|
| Tutorial / Guide / Knowledge | Pain-point scenario → core judgment → step-by-step method → common mistakes / limitations → one step you can do right away |
| Experience / Review / Store Visit | Usage scenario → specific observations → highlights and drawbacks → who it suits / who it does not suit → selection advice |
| Opinion / Trending Topic | Controversy or contrast → core judgment → reasons and examples → the other side / boundaries → a question left for readers |
| Personal Experience / Growth | Real struggle → turning point → what was done → observable change → transferable insight |
| Recommendation / Seeding / Event | Target audience and scenario → core value → specific reasons / experience → usage conditions and trade-offs |

<a id="成稿要求"></a>
## Final Draft Requirements

- First pin down the specific reader, scenario, and sense of gain; internally compare 3 titles—search-clarity type, pain-point resonance type, and contrast-curiosity type—and output only the strongest one that the body can deliver.
- The first screen uses 1–3 short paragraphs to complete "specific scenario / conflict → core judgment → content preview," and does not start from grand background or self-introduction.
- The body advances through short paragraphs and meaningful subheadings according to information increments; each section adds an action, observation, example, judgment, or limitation. The "human feel" comes from specific details, choices, and trade-offs, not from forcibly inserting internet-savvy words.
- Emoji can be used more actively than in formal genres, for navigation, tone, and pauses, but not stacked consecutively. Design the cover around one visual center, and place images / screenshots / diagrams near the corresponding content they serve; when no usable images are available, give brief image suggestions, and the body must still be independently readable.
- Core topic words naturally appear in the title or first screen, and related expressions enter subheadings and body as needed; hashtags are few and relevant, and are not repeated just to cover keywords.
- End with a memorable closing line; an interactive question is optional and at most one, with no fixed closing action required.

<a id="交付前检查"></a>
## Pre-delivery Check

Confirm that readers can tell at a glance "this is relevant to me," that the title promise has been delivered, that each section has substantive information, that it is easy to scan on a phone, and that emoji and images genuinely help understanding. Rework if there is officialese, long buildup, a wall of text, title-content mismatch, empty emotion, or fabricated facts.
