import {
  ArrowRight,
  Check,
  Clock3,
  FileCheck2,
  FileText,
  Fingerprint,
  GitPullRequest,
  ListChecks,
  Network,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";
import { shortHash, text, type Data, type Workspace } from "./api";
import { contextCoverage, contextTrail, type CoverageState } from "./workbench";
import { Empty, Panel, Status, SurfaceNotice, type T } from "./ui";
import type { Inspection } from "./App";
import type { MessageKey } from "./i18n";

const coverageKey: Record<CoverageState, MessageKey> = {
  unverified: "contextUnverified",
  "verified-declared-bindings": "contextBindingsMatch",
  incomplete: "contextIncomplete",
  conflict: "contextConflict",
};

type ContextProps = {
  t: T;
  workspace: Workspace | null;
  inspect: (value: Inspection) => void;
  expand: (title: string, value: unknown) => void;
};

export function ContextSignal({
  workspace,
  t,
  onOpen,
}: {
  workspace: Workspace | null;
  t: T;
  onOpen: () => void;
}) {
  const coverage = contextCoverage(workspace);
  const Icon =
    coverage.state === "conflict" || coverage.state === "incomplete"
      ? TriangleAlert
      : Network;
  return (
    <button
      className={`context-signal context-signal--${coverage.state}`}
      aria-label={`${t("openContext")}: ${t(coverageKey[coverage.state])}`}
      onClick={onOpen}
    >
      <Icon size={15} />
      <span>
        <small>{t("contextReadiness")}</small>
        <strong>{t(coverageKey[coverage.state])}</strong>
      </span>
      <ArrowRight size={13} />
    </button>
  );
}

export function ContextCoveragePanel(p: ContextProps) {
  const coverage = contextCoverage(p.workspace);
  const warning =
    coverage.state === "conflict" || coverage.state === "incomplete";
  return (
    <Panel
      title={p.t("contextReadiness")}
      icon={ShieldCheck}
      className="context-coverage-panel"
      onExpand={() => p.expand(p.t("contextReadiness"), coverage.record ?? {})}
      t={p.t}
      tools={
        <Status
          value={warning ? "pending" : "source_only"}
          label={p.t(coverageKey[coverage.state])}
        />
      }
    >
      <div
        className={`context-coverage-summary ${warning ? "has-context-gap" : ""}`}
      >
        <span className="context-coverage-icon">
          {warning ? <TriangleAlert size={21} /> : <Fingerprint size={21} />}
        </span>
        <div>
          <strong>{p.t(coverageKey[coverage.state])}</strong>
          <p>{p.t("contextBoundaryHelp")}</p>
        </div>
      </div>
      <div className="context-coverage-counters">
        <div>
          <FileCheck2 size={15} />
          <strong>
            {coverage.verifiedSources}
            <span> / {coverage.sources.length}</span>
          </strong>
          <small>{p.t("verifiedSources")}</small>
        </div>
        <div>
          <ListChecks size={15} />
          <strong>{coverage.missingMustIds.length}</strong>
          <small>{p.t("missingMusts")}</small>
        </div>
      </div>
      {coverage.manifestRef && (
        <button
          className="context-manifest-link"
          onClick={() =>
            p.inspect({
              title: coverage.manifestRef,
              kind: "context_manifest",
              data: coverage.record ?? {},
              sourcePath: coverage.manifestRef,
            })
          }
        >
          <FileText size={13} />
          <span title={coverage.manifestRef}>
            {coverage.manifestRef.split(/[\\/]/).pop()}
          </span>
          <code>{shortHash(coverage.manifestHash)}</code>
          <ArrowRight size={12} />
        </button>
      )}
      {coverage.missingMustIds.length + coverage.missingRequirementIds.length >
        0 && (
        <div className="context-gap-ids" aria-label={p.t("contextIncomplete")}>
          {[
            ...new Set([
              ...coverage.missingMustIds,
              ...coverage.missingRequirementIds,
            ]),
          ].map((id) => (
            <code key={id}>{id}</code>
          ))}
        </div>
      )}
      {coverage.issues.length > 0 && (
        <div className="context-issues">
          {coverage.issues.map((issue, index) => (
            <button
              key={`${issue.code ?? "issue"}-${index}`}
              onClick={() =>
                p.inspect({
                  title: text(issue.message ?? issue.code),
                  kind: "context_issue",
                  data: issue,
                  sourcePath: issue.path,
                })
              }
            >
              <TriangleAlert size={13} />
              <span>{text(issue.message ?? issue.code)}</span>
              <ArrowRight size={12} />
            </button>
          ))}
        </div>
      )}
      {coverage.sources.length > 0 ? (
        <div
          className="context-binding-list"
          aria-label={p.t("declaredBindings")}
        >
          {coverage.sources.map((source, index) => (
            <button
              className={`context-binding context-binding--${source.status}`}
              title={source.path}
              key={`${source.path}-${index}`}
              onClick={() =>
                p.inspect({
                  title: source.path || p.t("source"),
                  kind: "context_source",
                  data: source.record,
                  sourcePath: source.path || undefined,
                })
              }
            >
              <span className="context-binding-mark">
                {source.status === "verified" ? (
                  <Check size={14} />
                ) : (
                  <FileText size={14} />
                )}
              </span>
              <span className="context-binding-name">
                <strong>
                  {source.path.split(/[\\/]/).pop() || p.t("noDescription")}
                </strong>
                <small>
                  {source.required ? p.t("requiredSource") : p.t("source")}
                  {source.role ? ` · ${source.role}` : ""}
                </small>
              </span>
              <span
                className="context-binding-hash"
                title={`${p.t("expectedHash")}: ${source.expectedHash || "—"}\n${p.t("observedHash")}: ${source.observedHash || "—"}`}
              >
                <code>
                  {shortHash(source.observedHash || source.expectedHash)}
                </code>
                <Status
                  value={
                    source.status === "verified" ? "source_only" : "pending"
                  }
                  label={
                    source.status === "verified"
                      ? p.t("matched")
                      : source.status === "changed"
                        ? p.t("contextConflict")
                        : source.status === "missing"
                          ? p.t("unavailable")
                          : p.t("notTested")
                  }
                />
              </span>
              <ArrowRight size={12} />
            </button>
          ))}
        </div>
      ) : (
        <div className="panel-padding">
          <SurfaceNotice>{p.t("contextUnverified")}</SurfaceNotice>
        </div>
      )}
      {coverage.requirements.length > 0 && (
        <details
          className="context-requirement-bindings"
          open={warning || undefined}
        >
          <summary>
            <ListChecks size={14} />
            <strong>{p.t("requirements")}</strong>
            <span>{coverage.requirements.length}</span>
          </summary>
          <div>
            {coverage.requirements.map((requirement, index) => (
              <button
                key={`${requirement.requirement_id ?? "requirement"}-${index}`}
                onClick={() =>
                  p.inspect({
                    title: text(requirement.requirement_id),
                    kind: "context_requirement",
                    data: requirement,
                    sourcePath: requirement.source_path,
                  })
                }
              >
                <span>
                  <code>{text(requirement.requirement_id)}</code>
                  <small>
                    {text(requirement.source_path, p.t("sourceOnly"))}
                  </small>
                  {requirement.source_excerpt && (
                    <p>{text(requirement.source_excerpt)}</p>
                  )}
                </span>
                <Status
                  value={
                    requirement.status === "verified-excerpt"
                      ? "source_only"
                      : "pending"
                  }
                  label={
                    requirement.status === "verified-excerpt"
                      ? p.t("matched")
                      : p.t("notTested")
                  }
                />
                <ArrowRight size={12} />
              </button>
            ))}
          </div>
        </details>
      )}
    </Panel>
  );
}

export function ContextTrailPanels(p: ContextProps) {
  const trail = contextTrail(p.workspace);
  const list = (entries: Data[], kind: string) =>
    entries.length ? (
      <div className="context-trail-list">
        {entries.map((entry, index) => (
          <button
            key={entry.id ?? index}
            onClick={() =>
              p.inspect({
                title: text(entry.title ?? entry.summary ?? entry.id),
                kind,
                data: entry,
                sourcePath: entry.source_ref ?? entry.path,
              })
            }
          >
            <span>
              <strong>
                {text(
                  entry.title ?? entry.summary ?? entry.text ?? entry.id,
                  p.t("noDescription"),
                )}
              </strong>
              {(entry.id || entry.source_ref) && (
                <small>{text(entry.id ?? entry.source_ref)}</small>
              )}
            </span>
            <Status value={entry.status ?? "source_only"} />
            <ArrowRight size={12} />
          </button>
        ))}
      </div>
    ) : (
      <Empty compact title={p.t("noRecords")} />
    );
  return (
    <div className="context-trail-panels">
      <Panel
        title={p.t(trail.explicitlyCurrent ? "currentDecisions" : "decisions")}
        icon={GitPullRequest}
        tools={
          <span className="tag tag--subtle">{trail.decisions.length}</span>
        }
        onExpand={() =>
          p.expand(p.t("decisions"), p.workspace?.decisions ?? [])
        }
        t={p.t}
      >
        {list(trail.decisions, "decision")}
      </Panel>
      <Panel
        title={p.t("deferredWork")}
        icon={Clock3}
        tools={<span className="tag tag--subtle">{trail.deferred.length}</span>}
        onExpand={() => p.expand(p.t("deferredWork"), trail.deferred)}
        t={p.t}
      >
        {list(trail.deferred, "deferred_work")}
      </Panel>
    </div>
  );
}
