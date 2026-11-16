# App experience from intent to runtime

Contents include journeys, input and state, production, accessibility, commerce, and assembly.

## Causal experience

Read `cross-domain-core.md` and `app-system-contract.md`. Map accepted concept, domain, state, and API to intent → input → rule → feedback → durable result → next action. Cover first use, core and return, empty, loading and failure states, offline and conflict, cancel, undo and retry, interruption and recovery, permissions and account changes, export, deletion and support, and applicable payment. Each visible action binds to a domain command, response, and error contract. Keep unresolved backend capabilities explicit in the design.

Specify touch, mouse, keyboard and assistive input, selection and focus, gesture thresholds and priority, drag and cancel, navigation and deep links, timeouts and repeated taps. Define foreground and background, process death and reopening, unsaved work, stacked dialogs, and late callbacks. Animation reflects authoritative domain state. Give optimistic, pending, locally durable, and cloud-confirmed outcomes distinct feedback. Show critical payment or save confirmation after the defined authority confirms it.

## Platforms and state variants

Android, iOS, and web each complete the core journey. Identify parity and permitted platform-native differences. Specify expected layout and behavior for orientation, viewport, density, font scaling, safe areas, keyboard, back navigation, screen readers, and system permissions. Choose older-device coverage against the profile and feasible SDKs. Keep accepted originals, tokens, components, state variants, typography, copy, locales, and digests.

Derive idle, focused, pressed, disabled, loading, partial, success, error, blocked, and revoked states as applicable from the domain and data. Specify priority and interrupt or cancel rules for concurrent feedback. Preserve necessary information with reduced motion, mute, no haptics, or without color alone. Record out-of-scope media as absent_by_design. Add music or voice only where required.

## Reference feasibility and production

A concept frame represents a feasible layout, complexity, materials, and motion for its chosen route. Before accepting direction, show tool cost and limits, runtime support, and remaining manual craft. Image generation, editable vector or layered masters, tokens and assets, export and import, and actual screens are distinct operations. Background removal does not establish editable vector paths. Text in a raster requires separate localization and accessibility work. Verify operation capability, schema, and parameter consumption for each material property. Choose another feasible route for missing source, rig, or motion capabilities.

A recipe records accepted inputs and digests, tool and version, editable source, steps, export settings, runtime bindings, screen, state, device and locale scenario, and validators. Capture conversions for pixel density, typography, color and alpha, frames and seconds, locale grammar, accessible name, role and state, and focus order. Preserve the accepted master during downstream repair. Adjust the derivative or surface a material change for decision. For audio and motion, include source, session, timeline and events, looping, cancellation, lifecycle, perceptual checks, licenses, and applicable runtime budgets.

## Accessibility and content

Choose the relevant WCAG scope and level and native criteria from current official documentation. Automated checks cover a subset of conformance. Test names, roles and states, keyboard and focus, text scaling and reflow, contrast and noncolor cues, targets, failure identification and recovery, and reduced motion. Keep heuristic and synthetic checks, owner review, and real assistive or device observation separate. Respect current restrictions on participant recruitment or A/B testing. Test long text, plurals, number, date, time, and currency formats and RTL as relevant. Treat embedded raster text as a separate localization issue.

## Commerce and trust

Before payment, show scope, price, period, renewal, and limits. Preserve the agreed free or trial journey and post-purchase access. Define UI states for pending, refused, refunded, expired, restore, and account change. Check interacting offers, ads, and bundles together. Give external advertising its own clear meaning. Present deletion, reset, unlink, and disabling sync as distinct actions. For destructive actions, identify the actual subject and consequence.

## Acceptance on the medium

The first slice exercises real input and navigation, domain data, persistence and reopening, feedback, and applicable billing, sync, and support. Record exact build, config, assets, tokens and hashes, scenario, expectation and observation, target, viewport, input and accessibility settings. Compare runtime with accepted references using product-specific tolerances across platforms and GPUs. Test cold start, peak data, long strings, slow networks, and denied permission. Record static render, interactive prototype, and native evidence separately. Hand off masters, tokens, state map, content, rights, recipes, and runtime acceptance.

## Visible result and proportionality

Apply the [adaptive workflow](adaptive-work.md). Show interaction and state scenarios, meaningfully distinct design directions, accepted masters, prototype, and criteria for implementation fidelity. Distinguish completed work, inherited decisions, and future results with due gates. Scale depth and specialist involvement to uncertainty, consequence, and coupling. Use a local repair for a local change.

For material gaps, use the relevant [research, synthesis, or reconciliation mode](research-and-synthesis.md). Review language, visual quality, interaction, accessibility, and consistency across the experience. Inspect raw sources for omitted requirements. Verify reviewer competence beyond actor ID and keep structural checks at their actual evidence level. Preserve project context, current approvals, and unaffected results.
