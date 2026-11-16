# Commercial model, economy, and shop

## Applicability, inputs, and deliverables

Evaluate the business model alongside the game mechanics from concept. Add IAP, ads, or subscriptions only when the chosen scope calls for them. Read the fantasy and core loop, progression, reward, and world graphs, audience and markets, finite launch and release cadence, budget, and platform capabilities. Produce a comparison of models, the player-value journey, economy, catalogue and offer contracts, the shop state graph, and balance and integrity evidence. Use the [template](../../assets/domain-templates/commerce-player-journey.template.json). A deliberate `commerce.model:none` excludes the shop.

## Choose a model that fits the game

Compare relevant models against player value, frequency of use, content capacity, acquisition barriers, free and paid access, ongoing costs, and risks. Consider the applicable options among premium access, free trial and full unlock, expansions, optional alternative playstyles, cosmetics, finite resources or attempts or boosters, rewarded ads, passes, subscriptions, hybrids, and no offer. Treat owner examples as candidates for investigation within their stated authority.

Premium access can openly require purchase. For free-to-play, define a complete free progression arc and viable earned and decline paths. An expansion distinguishes base content, lifetime access, and new value. Cosmetics may suit the game. A requirement for alternative play calls for a distinct mechanical experience. Specify and test the cumulative advantage of alternate tools.

Study relevant successful and unsuccessful games in detail. Examine what they sell, when demand arises, what players reuse, what players can earn, and how limits, currency and reward loops, trials, shop behavior, and lifecycle work. Assess the effects of IP, marketing, and market conditions before drawing causal conclusions. Use the product's own observations for ARPU and retention claims.

## Connect offers to play and the shared economy

For each chosen offer, describe the sequence from desire through discovery, relevant trial or preview, earned/paid/decline choice, verified grant and ownership, repeated use, and a new meaningful objective. Compare baseline and alternative under the same circumstances, showing touch actions, changed decisions, limits and downsides, and effects on other systems. When same-run use is required, make the purchase available in the current campaign or save without a hidden reset or refill. Define trial eligibility and bounds.

For each resource and currency, define purpose, earned and paid provenance, sources, sinks and exchange, precision and caps, resets and refills, persistence and expiry, authority, UI, and dependencies. Distinguish ordinary resources, premium currency, entitlements, and experience access. Each additional currency needs a distinct role. Show the exact outcome and terms before spending.

For attempts or boosters, specify activity, baseline replenishment, eligible uses, spend order, maximum grants and uses per session, day, week, or event, stacking, duration, expiry, carryover, refunds, and the shared cap across earning, ads, and purchases. State the actual limit in rules, configuration, and player messages. Validate cap and entitlement invariants across time, offline use, and account changes.

For rewarded ads, define an optional trigger and the exact reward before viewing, frequency and fatigue caps, eligibility, loading, no-fill, offline, failure, cancellation, app suspend and return, verified completion, grant-once behavior, and reconciliation. Treat dismissal and earned reward as distinct callbacks. Provide a recovery path for system failures that preserves game outcomes and does not require viewing an ad.

For passes, subscriptions, and bundles, define exact contents, paid and free tracks where applicable, cadence, eligibility, claimed and unclaimed behavior, duplicates, renewals, cancellation and restoration, expiry, and entitlement life. If random rewards are selected, define pools, weights, version, guarantees, pity rules, and duplicates. Verify current rules and law for the specific market. Identify paid randomness from the actual commerce rules.

## Shop and transaction lifecycle

Define entry and discovery, categories and search where useful, preview, comparison and trial, owned/equipped/eligible/unavailable/locked states, exact contents, price, currency, duration and limits, confirmation and cancellation, pending/success/failure, and post-purchase use. Preserve the game's visual language. Localize prices using the platform's authoritative data. Decline and back actions are clear and preserve progress. Show genuine deadlines, accurate action labels, and visible renewal terms.

Model eligible, platform flow, pending/purchased/cancel/fail, verification, authoritative grant, acknowledgment or finishing, inventory and UI, and restore, reconciliation, refund and revocation. Define separate purchase, order, transaction, and grant IDs and a persistent deduplication key. Exercise duplicate and out-of-order callbacks, termination before and after the charge, offline return, account changes, parental approval, and consumed goods. Base financial authority on validated platform and server state as applicable. When an external purchase or upload outcome is unknown, reconcile it before retrying.

## Balance, operating costs, and evidence

Compare casual and skilled, new and returning, and paying and nonpaying players with equivalent playtime under the relevant model. Measure time to meaningful access, dominant strategies, collection and synergy advantages, bypassed limits, frustration barriers, inflation and stranded balances, exhaustion, and spending assumptions. Test the strongest combined paid portfolio as well as individual items. Assess situational power and cumulative advantage through actual decisions and outcomes. Keep difficulty and near-failure rules grounded in the accepted play experience.

Estimate net receipts, platform and ad fees, production, support, backend and QA costs, cadence capacity, and scenario uncertainty. Mark projections as scenarios until actual revenue is observed. Include the effort and any actual costs of organic acquisition.

Concepts needs model fit and causal value. Preproduction needs the typed economy, catalogue, journeys, caps, and boundaries. A slice tests applicable in-game discovery, decline, and use alongside honestly scoped simulated or sandbox processing. Schedule native, device, and purchase integration evidence for its due gate. Beta observes usefulness, comprehension, and voluntary choice with actual people. Release requires current platform policy, real sandbox receipts, and independent review of critical money and save behavior. Live operations needs actual cohorts, value and fairness observations, and support outcomes. Assign distinct deliverables to economy design, commerce and runtime engineering, UX, and independent review. Pricing and model decisions follow the owner's scope.

## Primary references

- Check current product, region, and age policy before release. Use legal authority for any legal determination. [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- Verify exact SDK and API requirements against the pinned integration version. [Google Play: one-time purchase lifecycle](https://developer.android.com/google/play/billing/lifecycle/one-time)
- Check official reward events and test integration, then assess whether ads suit the product. [Google AdMob: rewarded ads](https://developers.google.com/admob/android/rewarded)
- Comparative fit, shared caps, and cumulative counterexamples are agent checks. Actual commercial success requires independent research and product measurement.
