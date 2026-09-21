<a id="genre-contract-media--资讯媒体-routermedia"></a>
# Genre Contract: Media / News Media (`router.media`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Accurate, neutral, and compact; information density serves the reader's rapid understanding; do not substitute dramatic wording for factual strength |
| Content Logic | First determine the reader task of a news brief / report, explainer, profile, or interview; key information first, then evidence, necessary background, perspectives of relevant parties, and what remains unknown; paragraphs advance by importance, causality, or temporal relationship |
| Facts / Boundaries | Distinguish verified facts, source claims, inferences, and unknown; accuracy takes priority over being first to publish; key claims are traceable; negatively implicated parties get a reasonable opportunity to respond; quotations must be faithful and verifiable; images and source materials must have usage rights, provenance, contextual explanation, and textual equivalent information; corrections, disclosures, and key gaps must be directly visible; when core facts, source authenticity, or publication rights are missing, or when serious negative allegations have not yet been given an opportunity for response, keep it as a draft and blocked |
| Errors | Passing off an organization's own press release as independent reporting, headlines exceeding the evidence, a single anonymous source carrying major allegations, distorted quotations, mixing fact and commentary, omitting major opposing views or uncertainty, images without rights / provenance / textual equivalent information — any one of these constitutes failure |

<a id="适用与消歧"></a>
## Applicability and Disambiguation

This contract is for news content whose duty is independent gathering, verification, and public understanding. The appearance of "press release, media release, report" in a request serves only as a recall signal: when the editorial side can independently verify, choose the angle, and bear reporting judgment, use Media; press releases, brand statements, and PR messaging owned, approved, and released by an organization to the media or the public use Marketing.

When the primary purpose is persuasion from a stance, use Opinion; when the primary purpose is purchasing decisions and firsthand experience, use Consumer; internal factual briefings do not change their reader task just because they are written like news. Channel names, headline styles, or "write like the media" cannot trigger this on their own; when the final deliverable is explicitly required to be a Xiaohongshu note or a WeChat Official Account article, use `route_platform`, then select the corresponding leaf, with the news verification boundary serving as a hard constraint of that leaf contract.

<a id="子类型"></a>
## Subtypes

| Subtype | Reader Task and Progression |
|-|-|
| News Brief / Hard News | Know as quickly as possible what happened and how credible it is; core facts → sources and scope → necessary background → next confirmation point |
| Explainer Report | Understand why it happened, how it works, and where the controversy lies; question → mechanism / timeline → multi-party evidence → known boundaries |
| Profile / Feature | Understand a person or issue through verifiable scenes and experiences; scene → key change → evidence and others' perspectives → public significance |
| Interview / Q&A | Accurately obtain the interviewee's views and context; establish identity and setting, faithfully edit the Q&A, do not fabricate connecting remarks or stances |

<a id="证据与真实性"></a>
## Evidence and Authenticity

- Keep traceable materials for facts that may provoke controversy, recording source identity, how they are close to the facts, verification status, and usage restrictions; use anonymity only when there is public value and naming safely is impossible, and explain the source scope readers need for judgment.
- Quotations must be verifiable word for word; compression, translation, and paraphrase must not change the meaning. Numbers, times, identities, or causal relationships that cannot be confirmed should be marked unknown nearby; do not use "it is learned" or "sources say" to obscure source quality.
- For doxxing, cyberbullying, humiliation, minors, or other incidents that may amplify harm, retain only the minimum information needed to understand the facts, responsibility, and transmission mechanism; do not reproduce identity clues, offensive content, or unverified rumors just to prove a hot topic.
- Corrections must state what was changed; when new evidence changes the core judgment, update the headline and conclusion. Core claims that cannot be verified before publication must not be released by relying on placeholders.

<a id="结构与高质量写法"></a>
## Structure and High-Quality Writing

Headlines and leads promise only what the body has proven. Each paragraph carries one informational action, and on first appearance establishes the person, institution, time, and framing; background retains only the parts that change understanding. Multi-party statements are arranged by evidentiary weight rather than a formalistic tit-for-tat, neither writing verifiable facts as "both sides' views" nor writing an as-yet-unresolved matter as certain causation.
