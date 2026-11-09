import { useEffect, useState } from "react";
import {
  Archive,
  ArrowDownToLine,
  Check,
  Database,
  Eye,
  RefreshCw,
  ShieldCheck,
  Trash2,
} from "lucide-react";
import { rows, shortHash, text, type Data } from "./api";
import type { ViewProps } from "./views";
import type { MessageKey } from "./i18n";
import {
  Button,
  CodeViewer,
  Disclosure,
  Field,
  Panel,
  Status,
  SurfaceNotice,
} from "./ui";

const durations = [
  "event_days",
  "history_days",
  "input_cache_days",
  "backup_days",
] as const;
type Duration = (typeof durations)[number];
type Draft = Record<Duration, string>;
const durationLabels: Record<Duration, MessageKey> = {
  event_days: "eventRetention",
  history_days: "historyRetention",
  input_cache_days: "cacheRetention",
  backup_days: "backupRetention",
};
const countLabels: Record<string, MessageKey> = {
  associated_records: "associatedRecords",
  projects: "products",
  jobs: "jobs",
  tasks: "cleanupTasks",
  input_caches: "inputCaches",
  events: "cleanupEvents",
  receipts_redacted: "redactedReceipts",
  backups: "cleanupBackups",
  files: "cleanupFiles",
  bytes: "bytes",
};

function draftFrom(policy: Data | undefined): Draft {
  return Object.fromEntries(
    durations.map((key) => [
      key,
      policy?.[key] === null || policy?.[key] === undefined
        ? "retain"
        : String(policy[key]),
    ]),
  ) as Draft;
}

export function PrivacySettings(p: ViewProps) {
  const observed = p.boot?.retention as Data | undefined;
  const observedStamp = JSON.stringify(observed ?? null);
  const targetsStamp = JSON.stringify([
    p.boot?.projects.map((v) => v.id),
    p.boot?.jobs.map((v) => [v.id, v.status]),
    rows(p.boot?.tasks).map((v) => [v.id, v.paused]),
  ]);
  const [draft, setDraft] = useState<Draft>(() => draftFrom(observed));
  const [policyConfirmed, setPolicyConfirmed] = useState(false);
  const [projectIds, setProjectIds] = useState<string[]>([]);
  const [jobIds, setJobIds] = useState<string[]>([]);
  const [cleanup, setCleanup] = useState<Data | null>(null);
  const [cleanupConfirmed, setCleanupConfirmed] = useState(false);
  const [diagnostic, setDiagnostic] = useState<Data | null>(null);
  const [diagnosticConfirmed, setDiagnosticConfirmed] = useState(false);
  const [outcome, setOutcome] = useState<Data | null>(null);
  const [error, setError] = useState("");
  const [downloaded, setDownloaded] = useState("");
  const disabled = p.demo || Boolean(p.busy) || !observed;
  const valid = durations.every(
    (key) =>
      draft[key] === "retain" ||
      (/^\d+$/.test(draft[key]) &&
        Number(draft[key]) >= 1 &&
        Number(draft[key]) <= 3650),
  );
  const dirty = durations.some(
    (key) => draft[key] !== draftFrom(observed)[key],
  );
  const selected = projectIds.length + jobIds.length;

  function invalidate() {
    setCleanup(null);
    setCleanupConfirmed(false);
    setDiagnostic(null);
    setDiagnosticConfirmed(false);
    setOutcome(null);
    setDownloaded("");
    setError("");
  }
  useEffect(() => {
    setDraft(draftFrom(observed));
    setPolicyConfirmed(false);
    invalidate();
  }, [observedStamp]);
  useEffect(() => {
    const nextProjects = projectIds.filter((id) =>
      p.boot?.projects.some((v) => v.id === id),
    );
    const nextJobs = jobIds.filter((id) =>
      p.boot?.jobs.some(
        (v) =>
          v.id === id &&
          ["completed", "failed", "cancelled"].includes(v.status) &&
          !rows(p.boot?.tasks).find((task) => task.id === v.task_id)?.paused,
      ),
    );
    if (
      nextProjects.length !== projectIds.length ||
      nextJobs.length !== jobIds.length
    ) {
      setProjectIds(nextProjects);
      setJobIds(nextJobs);
      invalidate();
    }
  }, [targetsStamp]);

  function changeDuration(key: Duration, value: string) {
    setDraft((current) => ({ ...current, [key]: value }));
    setPolicyConfirmed(false);
    invalidate();
  }
  function toggleTarget(type: "project" | "job", id: string, checked: boolean) {
    const update = (ids: string[]) =>
      checked
        ? [...new Set([...ids, id])]
        : ids.filter((value) => value !== id);
    if (type === "project") setProjectIds(update);
    else setJobIds(update);
    invalidate();
  }
  async function run(operation: string, payload: Data = {}) {
    setError("");
    try {
      return await p.command(operation, payload);
    } catch (e) {
      setError((e as Error).message);
      return null;
    }
  }
  async function savePolicy() {
    const policy = Object.fromEntries(
      durations.map((key) => [
        key,
        draft[key] === "retain" ? null : Number(draft[key]),
      ]),
    );
    const result = await run("service.retention", {
      policy: { ...policy, automatic: false },
      confirmed: true,
    });
    if (result) {
      invalidate();
      setOutcome(result);
      setPolicyConfirmed(false);
    }
  }
  async function previewCleanup() {
    invalidate();
    const result = await run("service.cleanup-preview", {
      forget_project_ids: projectIds,
      forget_job_ids: jobIds,
    });
    if (result) setCleanup(result);
  }
  async function applyCleanup() {
    if (!cleanup || !cleanupConfirmed) return;
    const result = await run("service.cleanup-apply", {
      preview_id: cleanup.preview_id,
      sha256: cleanup.sha256,
      confirmed: true,
    });
    if (result) {
      invalidate();
      setProjectIds([]);
      setJobIds([]);
      setOutcome(result);
    } else {
      setCleanup(null);
      setCleanupConfirmed(false);
    }
  }
  async function previewDiagnostic() {
    setDiagnostic(null);
    setDiagnosticConfirmed(false);
    setDownloaded("");
    const result = await run("service.diagnostic-preview");
    if (result) setDiagnostic(result);
  }
  async function exportDiagnostic() {
    if (!diagnostic || !diagnosticConfirmed) return;
    const result = await run("service.diagnostic-export", {
      preview_id: diagnostic.preview_id,
      sha256: diagnostic.sha256,
      confirmed: true,
    });
    if (!result) {
      setDiagnostic(null);
      setDiagnosticConfirmed(false);
      return;
    }
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(result.content, null, 2) + "\n"], {
        type: "application/json",
      }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = text(result.filename, "agent-atelier-diagnostic.json");
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    setDownloaded(link.download);
    setDiagnostic(null);
    setDiagnosticConfirmed(false);
  }

  return (
    <section className="privacy-settings" aria-label={p.t("privacyStorage")}>
      <div className="privacy-settings__heading">
        <ShieldCheck size={20} />
        <div>
          <h2>{p.t("privacyStorage")}</h2>
          <p>{p.t("manualRetention")}</p>
        </div>
        <Status
          value={observed?.reviewed ? "observed" : "not_observed"}
          label={p.t(
            observed?.reviewed ? "policyReviewed" : "policyNotReviewed",
          )}
        />
      </div>
      <SurfaceNotice>{p.t("privacyBoundary")}</SurfaceNotice>
      <div className="settings-grid">
        <Panel title={p.t("retentionPolicy")} icon={Archive}>
          <div className="panel-padding">
            <p className="muted">{p.t("retentionHelp")}</p>
            <div className="retention-fields">
              {durations.map((key) => (
                <div className="retention-field" key={key}>
                  <Field label={p.t(durationLabels[key])}>
                    <input
                      type="number"
                      min={1}
                      max={3650}
                      step={1}
                      value={draft[key] === "retain" ? "" : draft[key]}
                      disabled={disabled || draft[key] === "retain"}
                      aria-label={p.t(durationLabels[key])}
                      data-retention={key}
                      onChange={(e) => changeDuration(key, e.target.value)}
                    />
                  </Field>
                  <label className="checkbox-field">
                    <input
                      type="checkbox"
                      checked={draft[key] === "retain"}
                      disabled={disabled}
                      data-retain={key}
                      onChange={(e) =>
                        changeDuration(
                          key,
                          e.target.checked
                            ? "retain"
                            : String(
                                observed?.[key] ??
                                  (key === "history_days" ||
                                  key === "backup_days"
                                    ? 90
                                    : 30),
                              ),
                        )
                      }
                    />
                    <span>{p.t("retainUntilSelected")}</span>
                  </label>
                </div>
              ))}
            </div>
            {!valid && (
              <SurfaceNotice tone="error">
                {p.t("retentionRange")}
              </SurfaceNotice>
            )}
            <label className="checkbox-field">
              <input
                type="checkbox"
                checked={policyConfirmed}
                disabled={disabled || !valid}
                data-policy-confirm
                onChange={(e) => setPolicyConfirmed(e.target.checked)}
              />
              <span>{p.t("confirmRetentionPolicy")}</span>
            </label>
            <Button
              icon={Check}
              onClick={() => void savePolicy()}
              disabled={disabled || !valid || !policyConfirmed}
              data-policy-save
            >
              {p.t("saveRetention")}
            </Button>
            {dirty && <p className="privacy-hint">{p.t("savePolicyFirst")}</p>}
          </div>
        </Panel>
        <Panel title={p.t("manualCleanup")} icon={Trash2}>
          <div className="panel-padding">
            <p className="muted">{p.t("cleanupHelp")}</p>
            <p className="privacy-hint">{p.t("cleanupLimits")}</p>
            <Disclosure title={p.t("forgetServiceHistory")}>
              <p className="muted">{p.t("forgetSelectionHelp")}</p>
              <div className="privacy-targets">
                {p.boot?.projects.map((project) => (
                  <label className="checkbox-field" key={project.id}>
                    <input
                      type="checkbox"
                      disabled={disabled}
                      checked={projectIds.includes(project.id)}
                      data-forget-project={project.id}
                      onChange={(e) =>
                        toggleTarget("project", project.id, e.target.checked)
                      }
                    />
                    <span>
                      <strong>{project.name}</strong>
                      <small>
                        {p.t("product")} · {shortHash(project.id)}
                      </small>
                    </span>
                  </label>
                ))}
                {p.boot?.jobs.map((job) => {
                  const task = rows(p.boot?.tasks).find(
                    (v) => v.id === job.task_id,
                  );
                  const eligible =
                    ["completed", "failed", "cancelled"].includes(job.status) &&
                    !task?.paused;
                  return (
                    <label className="checkbox-field" key={job.id}>
                      <input
                        type="checkbox"
                        disabled={disabled || !eligible}
                        checked={jobIds.includes(job.id)}
                        data-forget-job={job.id}
                        onChange={(e) =>
                          toggleTarget("job", job.id, e.target.checked)
                        }
                      />
                      <span>
                        <strong>
                          {text(job.objective ?? job.title, shortHash(job.id))}
                        </strong>
                        <small>
                          {shortHash(job.id)} · <Status value={job.status} />
                        </small>
                      </span>
                    </label>
                  );
                })}
                {!p.boot?.projects.length && !p.boot?.jobs.length && (
                  <p className="muted">{p.t("noRecords")}</p>
                )}
              </div>
            </Disclosure>
            {selected > 0 && (
              <p className="privacy-hint">
                {p.t("selected")} · {selected}
              </p>
            )}
            <Button
              icon={Eye}
              disabled={disabled || dirty || (!observed?.reviewed && !selected)}
              onClick={() => void previewCleanup()}
              data-cleanup-preview
            >
              {p.t("previewCleanup")}
            </Button>
            {cleanup && (
              <div className="cleanup-preview" data-cleanup-result>
                <div className="privacy-preview-id">
                  <ShieldCheck size={16} />
                  <code>{shortHash(cleanup.preview_id)}</code>
                  <code>{shortHash(cleanup.sha256)}</code>
                </div>
                <dl className="cleanup-counts">
                  {Object.entries(cleanup.counts ?? {}).map(([key, value]) => (
                    <div key={key}>
                      <dt>{countLabels[key] ? p.t(countLabels[key]) : key}</dt>
                      <dd>{text(value)}</dd>
                    </div>
                  ))}
                </dl>
                <Disclosure title={p.t("exactPlan")}>
                  <CodeViewer
                    value={cleanup}
                    fileName="cleanup-preview.json"
                    locale={p.locale}
                  />
                </Disclosure>
                <label className="checkbox-field">
                  <input
                    type="checkbox"
                    checked={cleanupConfirmed}
                    disabled={disabled}
                    data-cleanup-confirm
                    onChange={(e) => setCleanupConfirmed(e.target.checked)}
                  />
                  <span>{p.t("confirmCleanup")}</span>
                </label>
                <Button
                  tone="danger"
                  icon={Trash2}
                  disabled={disabled || !cleanupConfirmed}
                  onClick={() => void applyCleanup()}
                  data-cleanup-apply
                >
                  {p.t("applyCleanup")}
                </Button>
              </div>
            )}
            {rows(p.boot?.pending_cleanup).map((pending) => (
              <div className="privacy-pending" key={pending.id}>
                <SurfaceNotice>
                  {p.t("pendingCleanup")} · <code>{shortHash(pending.id)}</code>
                </SurfaceNotice>
                <Button
                  small
                  icon={RefreshCw}
                  disabled={disabled}
                  onClick={async () => {
                    const result = await run("service.cleanup-resume", {
                      cleanup_id: pending.id,
                    });
                    if (result) {
                      invalidate();
                      setOutcome(result);
                    }
                  }}
                >
                  {p.t("resumeCleanup")}
                </Button>
              </div>
            ))}
          </div>
        </Panel>
      </div>
      <Panel title={p.t("diagnosticExport")} icon={Database}>
        <div className="panel-padding">
          <p className="muted">{p.t("diagnosticHelp")}</p>
          <Button
            icon={Eye}
            disabled={disabled || dirty}
            onClick={() => void previewDiagnostic()}
            data-diagnostic-preview
          >
            {p.t("previewDiagnostic")}
          </Button>
          {diagnostic && (
            <div className="diagnostic-preview" data-diagnostic-result>
              <div className="privacy-preview-id">
                <ShieldCheck size={16} />
                <code>{shortHash(diagnostic.preview_id)}</code>
                <code>{shortHash(diagnostic.sha256)}</code>
              </div>
              <CodeViewer
                value={diagnostic.data}
                fileName="diagnostic-preview.json"
                locale={p.locale}
              />
              <label className="checkbox-field">
                <input
                  type="checkbox"
                  checked={diagnosticConfirmed}
                  disabled={disabled}
                  data-diagnostic-confirm
                  onChange={(e) => setDiagnosticConfirmed(e.target.checked)}
                />
                <span>{p.t("confirmDiagnostic")}</span>
              </label>
              <Button
                icon={ArrowDownToLine}
                disabled={disabled || !diagnosticConfirmed}
                onClick={() => void exportDiagnostic()}
                data-diagnostic-export
              >
                {p.t("downloadDiagnostic")}
              </Button>
            </div>
          )}
          {downloaded && (
            <SurfaceNotice>
              <Check size={15} /> {p.t("diagnosticSaved")} ·{" "}
              <code>{downloaded}</code>
            </SurfaceNotice>
          )}
        </div>
      </Panel>
      {outcome && (
        <Disclosure title={p.t("privacyReceipt")} initialOpen>
          <CodeViewer
            value={outcome}
            fileName="privacy-receipt.json"
            locale={p.locale}
          />
        </Disclosure>
      )}
      {error && (
        <SurfaceNotice tone="error">
          {error}
          <p>{p.t("cleanupRecovery")}</p>
        </SurfaceNotice>
      )}
    </section>
  );
}
