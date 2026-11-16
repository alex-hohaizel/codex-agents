# Camera, controls, learning and the complete player journey

## Applicability, inputs and owned outputs

Use for every interaction. Spatial camera rules apply to spatial play, and a fixed camera is a valid camera design. Start with the fantasy, core rules, target devices and orientation, world and encounters, progression and rewards, and creative boundaries. Deliver camera and input contracts, a screen and state atlas, learning curriculum, multimodal event map and usability scenarios. Use the [experience template](../../assets/domain-templates/camera-input-experience.template.json). Canonical domains `camera`, `input` and `learning` link to current project IDs.

## Camera behavior

Specify projection and view angle, tracking and follow behavior, focus, framing and subject scale, world bounds, orientation and aspect profiles. Evaluate fixed, follow, scroll, zone, over-the-shoulder, vehicle or other suitable modes with concrete benefits and risks. A side view may scroll and a full-scene reference does not determine the playable viewport.

For normal, traversal, aim, interaction, peak, transition or other needed states, specify triggers, targets and offsets, target subject fraction of the viewport, bounds, dead and soft zones, look-ahead, damping and velocity, zoom, occlusion, transition and cancellation, offscreen cues and return. Measure the hero's height as a viewport fraction and relate it to the action, viewing distance and visible upcoming challenge. Choose a genre-appropriate scale. Temporary variation is valid when predictable and when it preserves necessary information.

Check visibility margin before threats using closing speed, telegraph duration, camera travel, input latency, startup and opportunities to evade. Use distance and speed to diagnose the time to contact. Set and test response windows for the actual genre and audience. For offscreen attacks, reverse traversal, vertical changes, turns, pursuit and peak VFX, provide a readable cue or fair behavioral bound. Expand the view when it helps a decision while preserving functional character scale.

Show actual gameplay framing when comparing directions. If the mechanic requires camera movement, show a sequence of key states or footage within the claimed scope. Label a generated storyboard as a proposal. Carry accepted camera rules and framing into assets, implementation and QA.

## Controls that make depth accessible

For each input action define intent, gesture and device, context, hit area and ownership, thresholds and units, simultaneous contacts, priority and arbitration, hold, release and cancel, buffer, invalid reason, recovery and feedback. Link movement, aim, tools and camera input to phases of the governing rules. Preview the target and action for contextual inputs. Resolve ambiguity with a stable rule, explicit selection or safe cancellation.

Compare relevant control schemes on the same task, including one- and two-hand use, direct drag or steering, virtual controls, gestures, contextual actions and assist. Choose for genre, precision, pacing and comfort. Direction, timing, state, combinations of tools and position can create depth. Select controls for the decisions they enable.

Build a peak-load episode with movement, aim, action, tool changes, response and camera, finger obstruction and system edges. Specify concurrent and deliberately sequential actions. On an actual phone verify target reach, fatigue, different hand sizes, handedness, sensitivity, pause and interruption. Use touch observations for touch feel. Assist preserves purchased rights and must avoid forcing a weaker control scheme.

## Feedback, HUD and game feel

For important actions follow prediction, input, rule and contact, animation and VFX, SFX and music, haptic feedback, cost, reward or world change, and next decision. Specify latency, timing, cue priority, overlap, cooldown, intensity, interruption and owner. Cues warn, confirm, explain errors and support recovery. Essential information remains usable without audio or vibration, with reduced motion or effects, with appropriate color and contrast, and in supported locales.

Show state that informs the next decision, including value, range or trend, hazard, available action and recovery where relevant. Present health and resources as bars, discrete cues, diegetic signals or another readable representation. Tie each indicator to a decision and distinguish relevant systems. Test first-play, normal, peak and late-game states at phone size across aspect and font scales.

## Learning graph and the journey beyond core play

For each needed skill or system specify learning outcome, prerequisites, when it becomes relevant, cue, safe practice, assessment without continual hints, remediation and transfer. Verify independent mastery. Introduce nonessential systems when relevant and prioritize a comprehensible first action before inventory, store or resource complexity. Base assistance on observed error or delay, withdraw it after success and allow experienced players to continue. Specify skip, replay, practice and post-break resume without loss of progress.

Inventory first launch, loading, consent where required, hub and menus, settings and accessibility, tutorials and practice, selection, loadout, collection and upgrades, shop, play and pause, win, fail, reward and retry, unlock, offline and reconnect, suspend, resume and update, support, credits and applicable errors. Each reachable state has purpose, guard, data authority, visible content, actions and back behavior, pending, empty, locked and error states, effects, persistence and recovery. Add accounts and social systems only when the goal requires them. Reward or payment confirmation comes from authoritative state independently of animation.

## Interactions, evidence and roles

Camera and input change [world and actor fairness](world.md), [systems](systems.md), [learning and progression](progression.md), [creative](creative.md), commerce discovery and refusal, and save and resume. A hero scale change can affect telegraphs, encounters, HUD and performance. Reopen the affected evidence.

Concepts need causal camera, input and learning design plus first-play and peak examples. Preproduction needs typed values, state, transition and curriculum contracts and a measurement plan. The slice needs actual runtime measurements for input, camera and motion, native and device readability, and tactile and sound observations where access allows. Beta evaluates actual user errors, understanding, independent action, comfort and return with representative participants and scenarios. Release needs independent critical-state, purchase and save reviews and device verification. UX, input and camera authors, gameplay engineering, learning, accessibility and creative specialists share IDs. Independent review and actual playtests each serve their own purpose.

## Sources and status of recommendations

- [Roblox: Onboarding techniques](https://create.roblox.com/docs/production/game-design/onboarding-techniques) covers contextual tutorials, timed hints and feedback. Evaluate effectiveness in this game.
- [Nintendo: Wonder, chapter 3](https://www.nintendo.com/sg/interview/aqmx/03.html) illustrates accessible alternatives for progression and abilities.
- Camera contracts, visibility analysis and stage gates above are Game Atelier practices. Choose human performance targets for the actual game and participants.
