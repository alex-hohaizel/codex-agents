import { useEffect, useRef, useState, type FormEvent } from "react";
import { Image } from "lucide-react";
import { api, ApiError } from "./api";
import { Button, Field, SurfaceNotice, type T } from "./ui";

export function ImageGeneration({ csrf, t, projectId }: { csrf?: string; t: T; projectId?: string }) {
  const [phase, setPhase] = useState<"explore" | "implement" | "scratch">("implement");
  const [review, setReview] = useState<"" | "artifact" | "drift">("");
  const [blocked, setBlocked] = useState("");
  const [prompt, setPrompt] = useState("");
  const [artifact, setArtifact] = useState<Blob | null>(null);
  const [url, setUrl] = useState("");
  const [failure, setFailure] = useState<"" | "failed" | "unknown">("");
  const [running, setRunning] = useState(false);
  const pending = useRef(false);

  useEffect(() => {
    if (!artifact) {
      setUrl("");
      return;
    }
    const objectUrl = URL.createObjectURL(artifact);
    setUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [artifact]);

  async function generate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!csrf || prompt.trim().length < 3 || pending.current) return;
    pending.current = true;
    setRunning(true);
    setArtifact(null);
    setFailure("");
    setReview("");
    setBlocked("");
    try {
      const result = await api.generateImage(prompt.trim(), csrf,
        projectId && phase !== "scratch" ? { project_id: projectId, production_phase: phase } : undefined);
      if (
        result.status !== "completed" ||
        result.operation !== "codex.image.generate" ||
        result.artifact?.content_type !== "image/png" ||
        typeof result.artifact?.base64 !== "string"
      )
        throw new Error();
      const bytes = Uint8Array.from(atob(result.artifact.base64), (character) =>
        character.charCodeAt(0),
      );
      if (!bytes.length || bytes.length !== result.artifact.bytes)
        throw new Error();
      setArtifact(new Blob([bytes], { type: "image/png" }));
      if (projectId && phase !== "scratch") setReview(result.production_choice_state === "source-changed-review-required" ? "drift" : "artifact");
    } catch (error) {
      if (error instanceof ApiError && error.code === "PRODUCTION_CHOICE_REQUIRED") {
        setBlocked(error.message);
        return;
      }
      setFailure(
        error instanceof ApiError && error.code === "OUTCOME_UNKNOWN"
          ? "unknown"
          : "failed",
      );
    } finally {
      pending.current = false;
      setRunning(false);
    }
  }

  return (
    <form className="integrations-panel__media" onSubmit={generate}>
      <Field label={t("imageBrief")}>
        <textarea
          value={prompt}
          rows={4}
          minLength={3}
          maxLength={900}
          required
          disabled={running}
          onChange={(event) => setPrompt(event.target.value)}
        />
      </Field>
      {projectId && (
        <Field label={t("productionPhase")}>
          <select value={phase} disabled={running} onChange={(event) => {
            const next = event.target.value;
            if (next === "explore" || next === "implement" || next === "scratch") setPhase(next);
          }}>
            <option value="explore">{t("productionExplore")}</option>
            <option value="implement">{t("productionImplement")}</option>
            <option value="scratch">{t("productionScratch")}</option>
          </select>
        </Field>
      )}
      <div>
        <Button
          type="submit"
          icon={Image}
          disabled={!csrf || prompt.trim().length < 3 || running}
        >
          {t(running ? "running" : "imageGenerate")}
        </Button>
      </div>
      <p className="muted">{t("imageCodexUsage")}</p>
      {running && (
        <p className="muted" role="status">
          {t("running")}
        </p>
      )}
      {blocked && <div role="alert"><SurfaceNotice tone="error">{blocked}</SurfaceNotice></div>}
      {review && <SurfaceNotice tone="warning">{t(review === "drift" ? "productionDriftReview" : "productionArtifactReview")}</SurfaceNotice>}
      {failure && (
        <div role="alert">
          <SurfaceNotice tone="error">
            {t(failure === "unknown" ? "imageUnknown" : "imageFailed")}
          </SurfaceNotice>
        </div>
      )}
      {artifact && url && (
        <div className="integrations-panel__generated">
          <img src={url} alt={t("imagePreview")} />
          <a href={url} download="atelier-image.png">
            {t("download")} PNG
          </a>
        </div>
      )}
    </form>
  );
}
