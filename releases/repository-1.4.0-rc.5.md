# Repository 1.4.0-rc.5 and Agent Atelier 0.5.0

Opening the displayed next action carries its complete text into task preparation. The form keeps the current checkpoint action and preserves the reviewed fallback when the project has no declared action. Owners can edit the objective and acceptance before reviewing the route.

Connections can invoke OpenAI Docs MCP search and display official result links. Codex Image uses the existing ChatGPT login and the built-in tool when available. It previews and downloads the PNG returned for that run. Generation uses included Codex limits. Other native plugin actions use their host route when no direct operation is verified.

The panel uses the existing store format. [Update and rollback](migrations/repository-1.4.0-rc.5.md) · [Workbench guide](../apps/agent-atelier/README.md)

## Verification

The previous build reproduced an empty objective on the real project workbench. The corrected browser run passed 56 checks, including the full next action, edited acceptance, the prepared record in SQLite, and zero dispatched jobs. The integration browser run returned five official MCP links and downloaded a native 1536 × 1024 PNG from the same result shown in the preview. The desktop and mobile views passed nine integration checks. The local service suite passed 234 tests.

Managed connector execution stays in Codex where the host cannot verify the requested tool scope. The installed GitHub connector continued to advertise write tools in the scoped probe, so its managed action was not invoked. The existing direct GitHub CLI lookup is still available.
