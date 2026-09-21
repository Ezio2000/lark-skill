<a id="genre-contract-official-document--公文内容稿-workplaceofficial_redhead"></a>
# Genre Contract: Official Document / Official Document Content Draft (`workplace.official_redhead`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Solemn, accurate, concise, direct; no internet slang, marketing talk, emotional evaluation, empty talk, or mechanical numbering |
| Visual Strategy | Fixed `formal`; no highlight blocks, emoji, or decorative components |
| Allowed blocks | `title` (at most 1 for a complete document), `p`, `h1`, `h2`, `h3`, `h4`; heading levels must be continuous and no more than four levels |
| Use sparingly | `ul`, `ol` containers and `li` sub-blocks are only for genuine parallel items, not as a substitute for official document hierarchy numbering; `table` containers and `thead`, `tbody`, `tfoot`, `tr` sub-blocks are only for multi-object same-field information that is difficult to express clearly in a non-table format |
| Prohibited blocks | Types not listed in the allowed / use-sparingly lists are prohibited, including `callout`, `grid` containers and `column` sub-blocks, `checkbox`, `whiteboard`, `blockquote`, `pre`, root-level `code`, `hr`, `img`, `figure`; decorative colors, fake redheads, and fake seals are prohibited |
| Content Logic | Determine the single document genre based on the purpose of the communication, the relationship between agencies, and the audience, then proceed in the order of "necessary basis / reason → core matters / decisions → executable requirements → necessary closing" |
| Facts / Boundaries | Only write facts, bases, authority, and decisions that have been given or verified; use specific placeholders for unknown items; do not create when key gaps remain unclosed; Feishu only delivers a content review draft, and does not claim that it has been issued or taken effect |
| Errors | Prohibited: incorrect document genre or communication relationship, reports containing requests for instructions, requests for instructions covering multiple matters / multiple recipients, replies without a corresponding request for instructions, non-standard citations / document numbers / sequence numbers / attachments, and fabrication of facts, bases, authority, or issuance elements |

<a id="适用"></a>
## Applicability

Use only when an official document, redhead / red-seal format, or formal issuance is explicitly required, or when a statutory document genre appears together with agency communication relationships, document numbers, signatories, principal recipients, and other issuance elements. "Redhead document" is an issuance signal, not a document genre; ordinary company notices, policies, inspection / rectification materials go to `formal-doc.md`, and ordinary meeting records go to `meeting-minutes.md`.

<a id="文种选择"></a>
## Document Genre Selection

Judge by "purpose of communication → relationship between issuing and receiving agencies → audience scope", not by a single keyword.

| Document Genre | Applicable Intent |
|-|-|
| Resolution | Major decisions adopted through meeting discussion |
| Decision | Making deployment decisions, rewards or punishments, or changes / revocations regarding important matters |
| Order (Command) | Promulgating laws and regulations, implementing major coercive measures, conferring ranks, or issuing commendations |
| Communiqué | Authoritative publication of important decisions or major matters |
| Announcement | Announcing important or statutory matters to domestic and international audiences |
| Notice (Public) | Publishing matters that must be complied with or made known within a certain scope |
| Opinion | Offering views and handling methods on important issues |
| Notice | Requiring subordinates / relevant units to execute or be informed, or transmitting official documents with comments |
| Bulletin | Commending, criticizing, conveying important spirit, or informing of important situations |
| Report | Reporting work to superiors, reflecting situations, or answering inquiries, without requesting a decision |
| Request for Instructions | Requesting instructions or approval from superiors; one document for one matter, in principle sent to only one superior agency |
| Reply | Replying to a subordinate agency's request for instructions; there must be a corresponding incoming document |
| Proposal | The government submits to the people's congress at the same level or its standing committee for deliberation in accordance with the law |
| Letter | Negotiation, inquiry and reply, requesting approval, or replying to approval between agencies without a subordinate relationship |
| Minutes | Recording the main situations and decided matters of a formal meeting, without writing the verbatim process |

Priority disambiguation: for reporting without requesting a decision, use a report; for requesting a superior's decision, use a request for instructions; for negotiation between agencies without a subordinate relationship, use a letter; for execution by a clearly identified unit, use a notice; for compliance by unspecified recipients within a certain scope, use a public notice; for announcing important / statutory matters to domestic and international audiences, use an announcement; for conveying situations or evaluations, use a bulletin.

<a id="行文与事实"></a>
## Communication and Facts

- Communicate according to subordinate relationships, authority, and authorization; generally do not skip levels, and when skipping levels in special circumstances, simultaneously copy the skipped agency.
- Upward documents in principle are sent to one superior agency and are not copied to subordinates; reports must not carry requests for instructions. Except when directly assigned, do not address an individual superior as the principal recipient.
- One main document maintains one communication direction and authorization status; if the same matter requires both upward approval and downward execution requirements, split the document or issue it separately after approval; attachments must not smuggle in execution requirements that have not yet been authorized.
- Downward requirements must not exceed the authority of the issuing agency; when other regions' / departments' authority is involved, consult first. Joint issuance is limited to necessary situations with an appropriate subject relationship.
- Only write confirmed decisions as directives. Measures should specify, as needed, the subject, action, object, deadline, standard, and feedback destination; use wording matching the relationship, such as `商请`, `请予`, `函复`, for agencies without a subordinate relationship.
- Do not issue when authorization, key basis, core facts, scope of application, or approval decisions are lacking; do not guess document numbers, signatories, classification levels, or urgency levels.

<a id="内容结构"></a>
## Content Structure

- Titles generally use "issuing agency + subject matter + document genre"; when they contain the names of laws, regulations, or documents being issued, use title marks.
- Principal recipients use full names, standard abbreviations, or collective names for similar agencies. The attachment description must match the attachment order and names word for word; multiple attachments are numbered with Arabic numerals, and no punctuation is added at the end of names.

| Document Genre | Common Structure |
|-|-|
| Notice | Reason / basis → matters → object / time → confirmed requirements |
| Request for Instructions | Reason / basis → single requested matter and preferred opinion → `妥否，请批示` |
| Reply | Accurately cite the incoming document → clear opinion → execution requirements → `此复` |
| Letter | Matter / basis → negotiation request or reply → `请予函复` / `特此函复` |
| Report | Situation → facts / results → problems → follow-up arrangements → `特此报告` |
| Minutes | Basic meeting information → main situations → decided matters / responsibilities / time limits |

<a id="文号引用与序号"></a>
## Document Numbers, Citations, and Sequence Numbers

- Ordinary document numbers use "agency code + complete year + sequence number", such as `×政发〔2026〕8号`; the year uses hexagonal brackets, and the sequence number does not add "No." or pad with zeros. Order (Command) numbers may use `第×号`.
- When citing another official document for the first time, write the complete title and document number: `《××机关关于印发〈××办法〉的通知》（×发〔2026〕8号）`. Do not write only the document number, and do not use academic-style reference numbering.
- Use title marks for the names of documents, laws, and regulations; use Chinese double quotation marks for direct quotations, with single quotation marks for the inner layer. Quotations must be checked against the original text, validity, enacting agency, and scope of application; if they cannot be verified, mark `[引文待核]`.
- The body hierarchy uses `一、`, `（一）`, `1.`, `（1）` in order, and must not be written as `1、`, `（一）、`, and must not skip levels; when exceeding four levels, reorganize the content.
- The date of formation is written as `2026年7月13日`, with no zero padding for month and day. Punctuation and numerals follow GB/T 15834 and GB/T 15835; full names and standard abbreviations are consistent throughout.
