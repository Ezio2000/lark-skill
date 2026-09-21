<a id="genre-contract-data-report--数据报告-reportdata_report"></a>
# Genre Contract: Data Report (`report.data_report`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Accurate, reproducible, few adjectives; titles express findings, objects, and time points, and preserve uncertainty |
| Content Logic | First establish the metric contract and comparable baseline, then answer what happened, why it matters, and what cannot yet be asserted; observations, explanatory hypotheses, and action conditions are kept separate, and limitations are placed adjacent to the relevant conclusions |
| Facts / Boundaries | Core metrics must be labeled with definition, unit, numerator and denominator, population / segment, time window, source / version, update time, and revision status; comparisons must use the same methodology, estimates must disclose available uncertainty, and sensitive small groups must be aggregated, suppressed, or access-restricted; data charts must label axes, units, denominators, time points, and sources, and provide text-equivalent information |
| Errors | Listing only numbers; hiding denominators or methodology changes; ranking incomparable data; selective windows / segments; treating correlation as causation; missing chart axes, units, or sources; statistical significance masquerading as effect size or business victory; false precision; burying limitations in an appendix |

<a id="适用与消歧"></a>
## Applicability and Disambiguation

Interpret defined metrics, trends, distributions, funnels, monitoring, estimates, or experimental observations. `有数据`, `有数字`, and `分析一下` alone do not determine routing; research questions, sampling, and generalizability primarily go to [`research-report.md`](research-report.md), comparing business options goes to [`business-analysis.md`](business-analysis.md), and organizational status, deviations, and next steps go to Workplace periodic reports.

<a id="子类型"></a>
## Subtypes

- KPI / business performance and trends; segments, cohorts, and distributions; funnels / paths and monitoring anomalies.
- A/B or experimental readouts; when design and inference are insufficient, only observations may be reported, and causal victory must not be declared.
- Forecasts, estimates, revisions, or statistical briefs; must label model / assumptions, applicable period, and revision status.

<a id="证据与方法"></a>
## Evidence and Methods

- Preserve reproducible cardinality, filters, aggregations, estimation intervals, and quality notes; before comparing, verify definitions, populations, time windows, denominators, and processing methods.
- Based on risk of misinterpretation, provide absolute values, absolute changes, relative changes, and long-term baselines simultaneously; do not use excess decimal places to create a false sense of precision.
- If coverage, missingness, bias, methodology changes, and revisions would alter interpretation, they must appear alongside the corresponding findings, with possible direction, magnitude, and impact explained.
- Descriptive differences must not be written as causation; explanations are labeled as hypotheses to be verified. Statistical significance does not equal effect size, practical importance, or a complete basis for decision-making.
- When definitions, denominators, time, or sources are missing, use `[指标定义待核]` and `[分母待核]`, and the corresponding values must not enter conclusions; incomparable data is presented separately. When quality gaps on which core decisions depend cannot be closed, mark `blocked`.

<a id="结构与高质量写法"></a>
## Structure and High-Quality Writing

Key Findings and Decision Limitations → Metric Contract / Data Quality → Overview and Baseline → Necessary Dimensional Breakdowns, Distributions, and Counterexamples → Supportable Explanations and Hypotheses to Be Verified → Conditional Actions / Verification Gates → Methods, Revisions, and Sources. Each section advances as "Observation → Baseline / Context → Limitations → Implications"; complex charts must simultaneously provide textual conclusions and necessary precise values, and no visual may be the sole evidence.
