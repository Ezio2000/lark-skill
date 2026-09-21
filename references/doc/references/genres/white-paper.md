<a id="genre-contract-white-paper--白皮书-reportwhite_paper"></a>
# Genre Contract: White Paper (`report.white_paper`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Systematic, clear, restrained; authority comes from real entities, evidence, and attribution, not from length, formal tone, or visual complexity |
| Content Logic | First confirm the white paper type, publishing entity, professional readers, and expected judgment, then use evidence to establish the problem, evaluation criteria or framework, argumentation, counterexamples, and application boundaries; the framework must actually explain or compare |
| Facts / Boundaries | Objective claims connect to real sources, time points, scope, and limitations; facts, interpretations, value judgments, proposals, and brand positions can be distinguished; policy identity, publication status, interests, funding, and case selection must not be fabricated or concealed; evidence graphics and materials must confirm usage rights, sources, and explanations, and complex visuals must include textual equivalent information |
| Errors | Mixing policy and brand identity; titles or layouts that fabricate authority; grand background used to fill length; self-created frameworks used only as decoration; sources that cannot be traced; a single case passed off as consensus; ignoring counterevidence / conflicts of interest; CTA swallowing evidence; complex components replacing argumentation |

<a id="适用与消歧"></a>
## Applicability and Disambiguation

Enable professional readers to systematically understand and evaluate a problem, framework, or solution path. First distinguish government policy white papers from professional, technical, or brand-funded white papers issued by authorized entities; `白皮书`, `正式`, and `权威` alone do not create government or standards identity. When clarifying the research question and method is the core, go to [`research-report.md`](research-report.md); when deciding among options for a specific organization, go to [`business-analysis.md`](business-analysis.md); for design / RFC / interface contracts, go to Technical; when product selling points, customer acquisition, or CTA are primary, go to Marketing.

<a id="子类型"></a>
## Subtypes

- **Government Policy White Paper**: Only a genuinely authorized entity may use this; accurately mark policy, consultation, legislative, and publication status, and do not simulate approval or legal effect.
- **Policy / Professional Issue White Paper**: Form a reviewable argument around the problem, evidence, evaluation criteria, options, and impact.
- **Technical / Industry Landscape White Paper**: Explain technology, standards, or system frameworks; once the primary task is approving an implementation design or querying a precise contract, switch to Technical.
- **Brand-Funded White Paper**: Evidence evaluation must still be the primary task; disclose funding, product interests, and case selection, and separate conversion content from argumentation.

<a id="证据与边界"></a>
## Evidence and Boundaries

- At the beginning, clearly state the author / publishing entity, readers, use scenarios, scope, document status, core position, and expected judgment.
- Claim strength must match the evidence level; limited tests, correlational observations, vendor data, or a single case must not be expanded into absolute promises or industry consensus.
- Every layer of the framework must add explanatory, comparative, or selection value; problem causes, evaluation criteria, and solution logic must be connected, and important counterevidence, alternative explanations, and feasibility constraints must be addressed.
- When the entity or authorization is unclear, use `[发布主体待确认]`, and do not write it as government, official, or standards; when core evidence is insufficient, narrow it to a concept note / outline. For publication drafts where interest relationships or key policy status cannot be confirmed, mark `blocked`.

<a id="结构与高质量写法"></a>
## Structure and High-Quality Writing Approach

Standalone summary (entity, thesis, evidence boundaries) → problem and existing evidence → evaluation criteria or core framework → layer-by-layer argumentation, options, and counterexamples → application / policy implications and conditions → limitations, interest relationships, and sources. The summary should let busy readers restate the claims and retained conditions; only add a table of contents or appendix for long documents, and do not manufacture a sense of authority with background, cover, abbreviations, or components.
