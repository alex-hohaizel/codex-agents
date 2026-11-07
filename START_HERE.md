# Start here

Choose the language you want to read **and use with your agent**. Each link opens the full guide, including the complete installation and migration steps.

| Language | Full guide | Interaction preference |
| --- | --- | --- |
| English (default) | [Open](docs/en/GUIDE.md) | `preferred_language=en` |
| Українська | [Відкрити](docs/uk/GUIDE.md) | `preferred_language=uk` |
| Deutsch | [Öffnen](docs/de/GUIDE.md) | `preferred_language=de` |
| Italiano | [Apri](docs/it/GUIDE.md) | `preferred_language=it` |
| Español | [Abrir](docs/es/GUIDE.md) | `preferred_language=es` |
| Français | [Ouvrir](docs/fr/GUIDE.md) | `preferred_language=fr` |
| 简体中文 | [打开](docs/zh-CN/GUIDE.md) | `preferred_language=zh-CN` |

## Before installation

1. Sign in to the ChatGPT Work or Codex surface available to your account.
2. Enable the GitHub connection and grant `alex-hohaizel/codex-agents` access. Its current private visibility is preserved.
3. Open the full guide in your language. Copy its bootstrap request into a new skills-management conversation. That request includes the language preference and tells the agent to verify actual source and tools.
4. If repository access is unavailable in that host, download the repository while signed in to GitHub using **Code → Download ZIP**, extract it and provide the extracted folder through the host's supported file-access mechanism. The guide describes the fallback.
5. Follow the Work or Codex installation section. Verify source integrity, saved installation, actual discovery and a small task as distinct stages.

For a product you already work on, open its existing project and use the migration section. Keep its accepted requirements, identity and checkpoint. A new chat does not need a new product.

## Change the language later

Tell the agent: “Change preferred_language to [language code] in the current project context and use it for future explanations, clarification, progress, handoffs and installation advice. Keep API keys, code and stable identifiers unchanged.”

Persist the setting with [project context](templates/project-context.json), then carry it through every handoff. Browsing a translated README does not by itself persist a chat preference; the bootstrap request and saved context do.

[What the system does](README.md) · [Ten visual directions](marketing/README.md) · [Current release](releases/current.json)
