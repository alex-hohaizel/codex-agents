# Preserve visual identity

Use the `visual-identity/1` contract. A class describes purpose and origin, not release version or file count.

- `system` covers core constructors and families. The existing installed presentation and icons are accepted identity.
- `project` covers an agent or skill for a particular project. For a new icon where none exists, use `project-card-v1`: a light card with a clipped corner, teal accent, dark domain glyph and PROJECT strip. Pick a readable color and glyph for the purpose. Keep the style visually distinct from system skills.

Label new project-agent UI names with the established project designation, for example `Проєкт · …` when appropriate to the user. Preserve stable selectors. Change existing labels only within the authorized cosmetic scope.

## Update or repair

Preserve exact `interface.icon_small`, `icon_large`, `brand_color`, bindings and referenced bytes on a version change, move, repair or repackage. Preserve the actual local Codex appearance if it differs from Work. Snapshot paths and hashes before a change and compare after. Changes to `policy`, `dependencies`, `name`, executable files or unknown local files are separate impacts.

Report a conflicting path, symlink or missing asset. Recover the accepted original when possible. A version update does not authorize a redesign. An existing project agent keeps its inherited appearance even if it predates the current project class style.

## Create identity only where needed

Inspect the stable name, class, existing metadata and assets. Reuse and record existing icons. For a new project icon, `python3 -B scripts/visual_identity.py create-project --root SKILL_ROOT --glyph XX` creates a new SVG without editing UI metadata. Choose the domain-specific glyph, add both references in `agents/openai.yaml`, inspect legibility, and freeze approved assets. A two-letter glyph is a portable fallback.

For a new system skill, use an available real system example and a distinct domain mark. If no reference is available, state the gap and avoid claiming a match.

## Verify

Use `freeze --root SKILL_ROOT --class system|project` to record identity and byte hashes. Use `check --root SKILL_ROOT --lock SNAPSHOT.json` to compare without writing. Keep the snapshot in the current release or project registry outside skill discovery directories. The helper supports JSON and simple block YAML. Unknown complex metadata is a conflict rather than a guessed binding. Use an actual rendering for craft and legibility acceptance.
