import type { Project } from "./api";
import type { MessageKey } from "./i18n";
import type { View } from "./App";

export type Profile =
  | "app"
  | "bot"
  | "game"
  | "agent"
  | "research"
  | "document"
  | "mixed"
  | "generic";
export const profileDefinitions: Record<
  Profile,
  { title: MessageKey; skill: string; source: RegExp; order: View[] }
> = {
  app: {
    title: "applicationWorkbench",
    skill: "app-atelier-director",
    source: /api|contract|schema|prd|tdd|app-system/i,
    order: [
      "workspace",
      "requirements",
      "context",
      "identity",
      "artifacts",
      "evidence",
    ],
  },
  bot: {
    title: "chatbotWorkbench",
    skill: "chatbot-atelier-director",
    source: /conversation|persona|dialog|memory|knowledge|chatbot/i,
    order: [
      "workspace",
      "context",
      "identity",
      "requirements",
      "artifacts",
      "evidence",
    ],
  },
  game: {
    title: "gameWorkbench",
    skill: "gamedev-director",
    source: /game|gdd|mechanic|rule|art.direction|system/i,
    order: [
      "workspace",
      "identity",
      "requirements",
      "context",
      "artifacts",
      "evidence",
    ],
  },
  agent: {
    title: "agentWorkbench",
    skill: "agent-foundry",
    source: /blueprint|capabilit|skill|foundry|current.json/i,
    order: [
      "workspace",
      "requirements",
      "context",
      "evidence",
      "identity",
      "artifacts",
    ],
  },
  research: {
    title: "researchWorkbench",
    skill: "agent-foundry",
    source: /research|evidence|source|finding|hypothes/i,
    order: [
      "workspace",
      "context",
      "requirements",
      "evidence",
      "artifacts",
      "identity",
    ],
  },
  document: {
    title: "documentWorkbench",
    skill: "design-specialist-skills",
    source: /document|report|outline|deck|style|editorial/i,
    order: [
      "workspace",
      "artifacts",
      "context",
      "identity",
      "evidence",
      "requirements",
    ],
  },
  mixed: {
    title: "workspace",
    skill: "agent-foundry",
    source: /contract|blueprint|current.json/i,
    order: [
      "workspace",
      "context",
      "requirements",
      "identity",
      "artifacts",
      "evidence",
    ],
  },
  generic: {
    title: "workspace",
    skill: "agent-foundry",
    source: /contract|blueprint|current.json/i,
    order: [
      "workspace",
      "context",
      "requirements",
      "identity",
      "artifacts",
      "evidence",
    ],
  },
};
export function projectProfile(project: Project | null): Profile {
  const key = project?.view_profile ?? project?.kind ?? "generic";
  const aliases: Record<string, Profile> = {
    application: "app",
    chatbot: "bot",
    app: "app",
    bot: "bot",
    game: "game",
    agent: "agent",
    research: "research",
    document: "document",
    mixed: "mixed",
    generic: "generic",
  };
  return aliases[key] ?? "generic";
}
export function profileLabel(profile: Profile): MessageKey {
  return (
    {
      app: "application",
      bot: "chatbot",
      game: "game",
      agent: "agents",
      research: "research",
      document: "document",
      mixed: "generic",
      generic: "generic",
    } as const
  )[profile];
}
