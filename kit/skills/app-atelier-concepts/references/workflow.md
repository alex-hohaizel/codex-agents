# Concept and economics workflow

Contents include a complete concept card, commerce, the economic model, automated operations, selection, and handoff.

## 1. Build a complete concept card

Start from accepted research. Record candidate and requirement IDs, audience and payer, evidence claim IDs, specific user job, current alternative, gap, and reason to switch. Describe first and repeat useful sessions without requiring purchase. Match revisit patterns to the need's actual frequency. Define the core, explicit non-goals, clients, data, offline and degraded modes, and critical integrations. Set design direction, content and language, learning, errors and recovery, and defer exact design to its own acceptance. Differentiate candidates by problem-solving mechanism, workflow, cost structure, or business model.

## 2. Design free and paid use

Map need, first benefit, understood value, voluntary choice, granted result or entitlement, and repeat benefit. Retain the original example «потреба → перша користь → розуміння цінності → добровільний вибір → отримане право/результат → повторна користь». For each offer, define payer, billing unit, hypothesized price and currency, entitlement, timing, explanation, and limits. Compare relevant models against frequency of value, serving cost, and segment.

For free, trial and limited paths, show what is available, why and when limits apply, decline, result retention, and trial expiry. For subscriptions, define each period's value, source of updates or processing, renewal, cancellation, and post-expiry access. For usage pricing, define consumption unit, meter, cap, and exhausted behavior and make possible charges visible. For one-time unlock, model lifetime load and support, including ongoing API costs.

For ads, state formats, placement, opt-in rewards, frequency, disclosure, personalization permission, and fallback. Sell ad removal only to eligible ad-supported cohorts and account for the move from ad-funded to paid. For affiliates, record product value, disclosure, external terms, and compensation dependencies. Distinguish clicks from verified commissions. For team licenses, specify seats, roles, provisioning, self-service purchase and support, and feasibility of any manual sales. Contract entitlement, restore, refund and expiry without executing payment or other effects at concept stage.

## 3. Model economics for reproduction

Use the current profit definition, horizon, and currency. Where missing, ask the material scoped question and continue independent analysis. Each input has an ID, value or range and unknown, unit, period, geography, platform, cohort, source and date, kind and confidence. Keep tax-inclusive and tax-exclusive prices distinct. Verify current commissions, rates, and rules. Use exact decimal arithmetic and retain formulas, rounding, and conversions.

Distinguish launch costs, fixed monthly, variable usage and users, acquisition, refunds and chargebacks, and support. Include applicable hosting, storage and egress, API and AI, licenses, domains, store accounts, signing and toolchain, and monitoring. Track owner time and personal tax according to the accepted metric.

| Quantity | Calculation and limits |
|---|---|
| Net purchase revenue | Gross actual purchases minus applicable commissions, taxes or withholding, and refunds, with each deducted once. |
| Ad revenue | Eligible impressions × fill × eCPM / 1000. Apply fill only when impressions are eligible instead of already served. |
| Variable cost | Sum of consumption × applicable rate, including free tiers and step limits. |
| Contribution | Cohort net revenue minus variable cost. Include serving costs for free users. |
| Operating profit | Sum of cohort contribution minus fixed operating and acquisition costs within the accepted definition. |
| Required active scale | For stable positive contribution per active user: ceil((target + fixed cost) / contribution_per_active). Use the full model otherwise. |

Recalculate for zero or negative margin, step costs, or changed cohort mix. Tie one-time revenue to new payers and permitted repeat purchases instead of the installed base. For annual payments, separate cash flow and monthly recognition. Model subscription cohorts through acquisition, activation, conversion, retention or churn, and renewals. Keep unknown churn explicit. Deduplicate revenue across web, stores, subscriptions and modules and specify upgrades and credits. Use cohort contribution, horizon and retention limits for LTV where ARPU and churn alone are inadequate.

Build justified low, base and high scenarios under consistent definitions and distinguish scenarios from probability forecasts. Test relevant sensitivity to payment, usage, ad yield, API cost, conversion, churn, and acquisition. State what must be true to reach the target and compare required scale with reachable payers. Model cash runway, upfront cost, free tier cutoffs, settlement timing and minimums, working-capital deficits and stop before revenue. Surface required upfront funding independently of projected revenue.

## 4. Verify automated operations

Map process, trigger, tool or provider, data and rights, frequency and cost, failure and unknown outcome, fallback and stop, and permitted human involvement. Include acquisition, content and data, onboarding, payment, support, moderation, updates, deletion, and retirement. Honor limits on recurring owner work including blogging, sales, translation, AI-response review and moderation. Separate one-off MFA or legal prerequisites from daily operations.

Cover automation edge cases, outages, exhausted budgets, disputes, and unknown effects. Treat repeated manual dependencies as risks or rejection grounds. Hand product-specific support facts, rules, tone, and data needs to the separate support bot role. Preserve isolation from other bots and their private memory.

## 5. Select and hand off

Check mandatory requirements individually, including competitive exceptions and restrictions on human experiments. Score only eligible candidates and separate fit, evidence strength, and uncertainty. Define continue, pivot, and stop for each allowed step before the result. Give the owner comparable cost, benefit, downside, critical unknowns, and recommendation, including rejection of all options.

Hand off the accepted candidate, model, operations and acquisition briefs, prototype scenarios, evidence hashes, and open decisions. Test normal and failed paths, onboarding, free and paid transition, technical risks, and observable quality in any prototype. Verify actual interaction independently of static renders. Before significant build, establish accepted scope and design, early release feasibility, growth plan, and an observed representative slice.

## Visible result and proportionality

Apply the [adaptive workflow](adaptive-work.md). Show the complete concept, causal user and commerce journeys, system design, production feasibility and alternatives. Distinguish completed work, inherited decisions, and due future results. Scale depth and roles to uncertainty, consequence, and coupling. Use a local repair for a local change.

For material gaps, use the relevant [research, synthesis, or reconciliation mode](research-and-synthesis.md). Review whole experience, strongest counterargument, and economic assumptions. Inspect raw inputs for omissions. Verify reviewer competence beyond actor ID and keep structural checks at their actual evidence level. Preserve context, approvals, and unaffected results.
