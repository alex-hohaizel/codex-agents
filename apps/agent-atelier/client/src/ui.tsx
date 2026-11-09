import { useEffect, useRef, useState, useContext, type ReactNode } from "react";
import {
  Check,
  CheckCheck,
  ChevronDown,
  ChevronRight,
  Copy,
  FileText,
  Maximize2,
  X,
  type LucideIcon,
} from "lucide-react";
import { pretty, shortHash, text, type Data } from "./api";
import { LocaleContext, translate, type MessageKey } from "./i18n";

export type T = (key: MessageKey) => string;

export function Button({
  children,
  icon: Icon,
  tone = "default",
  small,
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  icon?: LucideIcon;
  tone?: "default" | "primary" | "danger" | "quiet";
  small?: boolean;
}) {
  return (
    <button
      className={`button button--${tone} ${small ? "button--small" : ""} ${className}`}
      type="button"
      {...props}
    >
      {Icon && <Icon size={small ? 14 : 16} strokeWidth={1.7} />}
      {children}
    </button>
  );
}

export function IconButton({
  icon: Icon,
  label,
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  icon: LucideIcon;
  label: string;
}) {
  return (
    <button
      type="button"
      className={`icon-button ${className}`}
      aria-label={label}
      title={label}
      {...props}
    >
      <Icon size={16} strokeWidth={1.7} />
    </button>
  );
}

export function Panel({
  title,
  icon: Icon,
  children,
  tools,
  className = "",
  subtitle,
  onExpand,
  t,
}: {
  title: string;
  icon?: LucideIcon;
  children: ReactNode;
  tools?: ReactNode;
  className?: string;
  subtitle?: string;
  onExpand?: () => void;
  t?: T;
}) {
  return (
    <section className={`panel ${className}`}>
      <header className="panel__header">
        <div className="panel__heading">
          {Icon && <Icon size={15} strokeWidth={1.7} />}
          <h2>{title}</h2>
          {subtitle && <span className="panel__subtitle">{subtitle}</span>}
        </div>
        <div className="panel__tools">
          {tools}
          {onExpand && (
            <IconButton
              icon={Maximize2}
              label={t?.("fullscreen") ?? "Expand"}
              onClick={onExpand}
            />
          )}
        </div>
      </header>
      {children}
    </section>
  );
}

const good = new Set([
  "accepted",
  "completed",
  "pass",
  "passed",
  "ready",
  "connected",
  "success",
  "active",
  "observed",
  "verified",
  "available",
  "healthy",
]);
const bad = new Set([
  "failed",
  "fail",
  "error",
  "blocked",
  "stale",
  "conflict",
  "declined",
  "outcome_unknown",
]);
const active = new Set([
  "running",
  "queued",
  "dispatching",
  "prepared",
  "pending",
  "cancel_requested",
  "awaiting_approval",
  "awaiting_input",
  "reconciling",
]);
export function statusTone(
  value: unknown,
): "good" | "bad" | "active" | "neutral" {
  const s = String(value ?? "").toLowerCase();
  return good.has(s)
    ? "good"
    : bad.has(s)
      ? "bad"
      : active.has(s)
        ? "active"
        : "neutral";
}
export function Status({
  value,
  label,
  dot = true,
}: {
  value?: unknown;
  label?: string;
  dot?: boolean;
}) {
  const locale = useContext(LocaleContext);
  const keyByStatus: Record<string, MessageKey> = {
    source_only: "sourceOnly",
    not_observed: "unknown",
    not_tested: "notTested",
    not_checked: "notTested",
    unverified: "notTested",
    ready: "ready",
    blocked: "blocked",
    observed: "observed",
    running: "running",
    completed: "completed",
    failed: "failed",
    pending: "pending",
    accepted: "accepted",
    cancelled: "cancelled",
    cancel_requested: "cancelRequested",
    paused: "paused",
    deferred: "deferred",
    connected: "connected",
    disconnected: "disconnected",
    example_only: "exampleOnly",
    source: "sourceOnly",
    needs_review: "pendingReview",
    review_pending: "pendingReview",
    unavailable: "unavailable",
    not_connected: "notConnected",
  };
  const readable = keyByStatus[String(value)]
    ? translate(locale, keyByStatus[String(value)])
    : text(value);
  return (
    <span
      className={`status status--${statusTone(value)}`}
      title={String(value ?? "")}
    >
      {dot && <span className="status__dot" />}
      {label ?? readable}
    </span>
  );
}

export function Empty({
  icon: Icon = FileText,
  title,
  children,
  action,
  compact,
}: {
  icon?: LucideIcon;
  title: string;
  children?: ReactNode;
  action?: ReactNode;
  compact?: boolean;
}) {
  return (
    <div className={`empty ${compact ? "empty--compact" : ""}`}>
      <div className="empty__symbol">
        <Icon size={24} strokeWidth={1.2} />
      </div>
      <h3>{title}</h3>
      {children && <p>{children}</p>}
      {action && <div className="empty__action">{action}</div>}
    </div>
  );
}

export function CodeViewer({
  value,
  fileName,
  language = "json",
  selectedLine,
  locale = "uk",
  onInspect,
}: {
  value: unknown;
  fileName?: string;
  language?: string;
  selectedLine?: number;
  locale?: string;
  onInspect?: () => void;
}) {
  const [copied, setCopied] = useState(false);
  const content = pretty(value);
  const lines = content.split("\n");
  async function copy() {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    } catch {
      setCopied(false);
    }
  }
  return (
    <div className="code-viewer">
      <div className="code-viewer__bar">
        <span>
          <FileText size={13} />
          {fileName ?? language}
        </span>
        <div>
          <span className="code-language">{language.toUpperCase()}</span>
          <IconButton
            icon={copied ? Check : Copy}
            label={translate(locale, copied ? "copied" : "copy")}
            onClick={copy}
          />
          {onInspect && (
            <IconButton
              icon={Maximize2}
              label={translate(locale, "fullscreen")}
              onClick={onInspect}
            />
          )}
        </div>
      </div>
      <div
        className="code-viewer__scroll"
        tabIndex={0}
        aria-label={fileName ?? language}
      >
        <pre>
          {lines.map((line, index) => (
            <div
              key={index}
              className={`code-line ${selectedLine === index + 1 ? "code-line--selected" : ""}`}
            >
              <span className="code-line__number" aria-hidden="true">
                {index + 1}
              </span>
              <code>{highlight(line)}</code>
            </div>
          ))}
        </pre>
      </div>
    </div>
  );
}

function highlight(line: string): ReactNode[] {
  return line
    .split(
      /("(?:[^"\\]|\\.)*"|'[^']*'|\b(?:true|false|null|undefined)\b|\b\d+(?:\.\d+)?\b|#[^\n]*$)/g,
    )
    .filter(Boolean)
    .map((part, i) => {
      let type = "";
      if (/^"/.test(part)) type = "string";
      else if (/^'/.test(part)) type = "string";
      else if (/^(true|false|null|undefined)$/.test(part)) type = "literal";
      else if (/^\d/.test(part)) type = "number";
      else if (/^#/.test(part)) type = "comment";
      return (
        <span className={type ? `syntax-${type}` : undefined} key={i}>
          {part}
        </span>
      );
    });
}

export function RecordDetails({
  value,
  t,
  compact = false,
}: {
  value: Data;
  t: T;
  compact?: boolean;
}) {
  const entries = Object.entries(value).filter(
    ([key, value]) =>
      value !== undefined &&
      value !== null &&
      ![
        "content",
        "output",
        "events",
        "messages",
        "source_text",
        "text",
        "description",
        "summary",
      ].includes(key),
  );
  return (
    <dl
      className={`record-details ${compact ? "record-details--compact" : ""}`}
    >
      {entries.slice(0, compact ? 8 : 24).map(([key, value]) => (
        <div key={key}>
          <dt>
            {key in
            {
              id: 1,
              status: 1,
              phase: 1,
              scope: 1,
              author: 1,
              reviewer: 1,
              version: 1,
              method: 1,
              environment: 1,
              subject: 1,
              root: 1,
              revision: 1,
              kind: 1,
              name: 1,
              source: 1,
              state: 1,
              endpoint: 1,
              host: 1,
            }
              ? translateKey(key, t)
              : key.replaceAll("_", " ")}
          </dt>
          <dd>
            {typeof value === "object" ? (
              <pre>{pretty(value)}</pre>
            ) : /hash|digest|revision/.test(key) ? (
              <code title={text(value)}>{shortHash(value)}</code>
            ) : (
              text(value)
            )}
          </dd>
        </div>
      ))}
    </dl>
  );
}

function translateKey(key: string, t: T): string {
  const map: Record<string, MessageKey> = {
    id: "key",
    status: "status",
    phase: "phase",
    scope: "scope",
    author: "author",
    reviewer: "reviewer",
    version: "version",
    method: "method",
    environment: "environment",
    subject: "subject",
    root: "projectRoot",
    revision: "revision",
    kind: "kind",
    name: "projectName",
    source: "source",
    state: "state",
    endpoint: "endpoint",
    host: "host",
  };
  return t(map[key] ?? "key");
}

export function Modal({
  title,
  children,
  onClose,
  footer,
  wide = false,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
  footer?: ReactNode;
  wide?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  // Capture the opener before child autoFocus runs during the commit.
  const returnFocus = useRef<HTMLElement | null>(
    typeof document !== "undefined" &&
      document.activeElement instanceof HTMLElement
      ? document.activeElement
      : null,
  );
  const locale = useContext(LocaleContext);
  useEffect(() => {
    const d = ref.current;
    if (d && !d.open) d.showModal();
    const focusFrame = requestAnimationFrame(() => {
      if (d?.open) d.querySelector<HTMLElement>("[data-autofocus]")?.focus();
    });
    return () => {
      cancelAnimationFrame(focusFrame);
      if (d?.open) d.close();
      if (returnFocus.current?.isConnected)
        returnFocus.current.focus({ preventScroll: true });
    };
  }, []);
  return (
    <dialog
      ref={ref}
      className={`modal ${wide ? "modal--wide" : ""}`}
      onKeyDown={(event) => {
        if (event.key !== "Tab") return;
        const dialog = event.currentTarget;
        const controls = Array.from(
          dialog.querySelectorAll<HTMLElement>(
            'button:not([disabled]),a[href],input:not([disabled]):not([type="hidden"]),select:not([disabled]),textarea:not([disabled]),[tabindex]',
          ),
        ).filter(
          (node) => node.tabIndex >= 0 && node.getClientRects().length > 0,
        );
        event.preventDefault();
        const current = controls.indexOf(document.activeElement as HTMLElement);
        const next =
          current < 0
            ? event.shiftKey
              ? controls.length - 1
              : 0
            : (current + (event.shiftKey ? -1 : 1) + controls.length) %
              controls.length;
        (controls[next] ?? dialog).focus();
      }}
      onCancel={(e) => {
        e.preventDefault();
        onClose();
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <header className="modal__header">
        <h2>{title}</h2>
        <IconButton
          icon={X}
          label={translate(locale, "close")}
          onClick={onClose}
        />
      </header>
      <div className="modal__body">{children}</div>
      {footer && <footer className="modal__footer">{footer}</footer>}
    </dialog>
  );
}

export function Disclosure({
  title,
  children,
  initialOpen = false,
}: {
  title: string;
  children: ReactNode;
  initialOpen?: boolean;
}) {
  return (
    <details className="disclosure" open={initialOpen || undefined}>
      <summary>
        <ChevronRight size={14} />
        <span>{title}</span>
        <ChevronDown size={13} />
      </summary>
      <div>{children}</div>
    </details>
  );
}

export function ProgressSteps({
  labels,
  current = 0,
}: {
  labels: string[];
  current?: number;
}) {
  return (
    <ol className="progress-steps">
      {labels.map((label, i) => (
        <li
          key={label}
          className={
            i < current ? "is-done" : i === current ? "is-current" : ""
          }
        >
          <span>{i < current ? <CheckCheck size={14} /> : i + 1}</span>
          <p>{label}</p>
        </li>
      ))}
    </ol>
  );
}

export function Field({
  label,
  help,
  children,
}: {
  label: string;
  help?: string;
  children: ReactNode;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
      {help && <small>{help}</small>}
    </label>
  );
}

export function SurfaceNotice({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "warning" | "error" | "good";
}) {
  return (
    <div className={`surface-notice surface-notice--${tone}`}>{children}</div>
  );
}
