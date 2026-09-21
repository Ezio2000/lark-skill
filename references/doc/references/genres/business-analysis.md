<a id="genre-contract-business-analysis--商业分析-reportbusiness_analysis"></a>
# Genre Contract: Business Analysis (`report.business_analysis`)

<a id="体裁规则表硬约束"></a>
## Genre Rules Table (Hard Constraints)

| Rule Item | Rule |
|-|-|
| Writing Style | Conclusion-first, specific, conditional; models are used only to change comparisons or expose constraints, not to replace judgment with management jargon |
| Content Logic | Centered on one specific decision, compare the status quo / no action against real alternatives; evaluate value, full-lifecycle cost, risk, constraints, and implementability using a unified objective and consistent basis, and give a recommendation, deferral, or validation gate with flip conditions |
| Facts / Boundaries | Separate facts, estimates, assumptions, unknowns, and external dependencies; label numbers with source, time point, unit, basis, and confidence range; stakeholders, non-monetizable impacts, and authority boundaries are prominent; analysis recommendations do not equal approval or commitment |
| Errors | Finding arguments for a preselected option; no status quo baseline or real alternatives; ranking with inconsistent bases; replacing balanced judgment with a single ROI / BCR / score; applying SWOT as a template; passing estimates off as facts; ignoring full-lifecycle cost, dependencies, or distributional impacts; writing unapproved items as committed; recommendations not linked back to evidence |

<a id="适用与消歧"></a>
## Applicability and Disambiguation

Compare investment, resource, market, product, operational, or supply options and support judgment, but the main text does not require a named decision-maker to make a choice / approval, nor does it form an entry point for authorization, resource allocation, or execution commitment. `商业`, `市场分析`, and `SWOT` are used only for recall on their own; for answering research questions go to [`research-report.md`](research-report.md), for pure metric interpretation go to [`data-report.md`](data-report.md), when the above ask / authorization entry points are hit go to Workplace Proposal, and when interfaces, invariants, and implementation trade-offs are primary go to Technical RFC.

<a id="子类型"></a>
## Subtypes

Investment / resource allocation; build-buy-partner or vendor; market entry / expansion; product / portfolio prioritization; operating model / process; pricing / business model; high-uncertainty pilots or stage gates. Analysis depth increases with amount, complexity, irreversibility, scope of impact, and risk.

<a id="证据与方法"></a>
## Evidence and Method

- Define the problem, objective, success criteria, scope, constraints, decision owner / timing, and status quo / no-action baseline; record option generation and exclusion rationale.
- For each viable option, compare benefits, full-lifecycle cost, time, capabilities / dependencies, risk, affected parties, non-monetizable impacts, and reversibility using the same dimensions.
- Separate status quo data from forecasts; explain currency, price time point, discounting, and estimation method as needed. Do not infer sales, revenue, or share from official website list prices.
- Conduct range, scenario, or sensitivity analysis on assumptions that could flip the conclusion, and give switching values, decision gates, or validation signals; scoring models must explain weights and evidence, not just report a total score.
- When objectives, success criteria, baselines, or viable options are missing, produce only a decision frame / options discovery; use `[成本区间待核]` and a validation plan for key estimates, and mark `blocked` when something could flip the conclusion and cannot be bounded.

<a id="结构与高质量写法"></a>
## Structure and High-Quality Writing

Recommendation and conditions → case for change / objective / status quo baseline → option generation, exclusion rationale, and same-basis comparison → key assumptions, risks, scenarios, and flip conditions → why the recommendation is better than alternatives → stage gates, monitoring / learning plan, and open conditions. Treat the status quo as a real option, replace false-precision point estimates with ranges and scenarios, and prominently explain who benefits, who bears the cost, and what new evidence would change the recommendation.
