const VERSION_NUMBER = "(?:0|[1-9]\\d*)";
const PRERELEASE_ID = "(?:0|[1-9]\\d*|\\d*[A-Za-z-][A-Za-z0-9-]*)";
const SEMVER = new RegExp(
  `^${VERSION_NUMBER}\\.${VERSION_NUMBER}\\.${VERSION_NUMBER}` +
    `(?:-${PRERELEASE_ID}(?:\\.${PRERELEASE_ID})*)?` +
    "(?:\\+[A-Za-z0-9-]+(?:\\.[A-Za-z0-9-]+)*)?$",
);

export function skillVersion(raw, fallback = "unknown") {
  const frontmatter = /^---[ \t]*\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/.exec(
    raw,
  )?.[1];
  const lines = frontmatter?.split(/\r?\n/) ?? [];
  const metadata = [];
  const start = lines.findIndex((line) =>
    /^metadata:[ \t]*(?:#.*)?$/.test(line),
  );
  if (start >= 0) {
    // Look only at direct children of the leading metadata block, not examples or nested keys.
    for (const line of lines.slice(start + 1)) {
      if (/^[ \t]*(?:#.*)?$/.test(line)) continue;
      if (!line.startsWith(" ")) break;
      metadata.push(line);
    }
    const indent = metadata.reduce(
      (minimum, line) =>
        Math.min(minimum, line.length - line.trimStart().length),
      Infinity,
    );
    const fields = metadata
      .filter((line) => line.length - line.trimStart().length === indent)
      .map((line) => line.slice(indent))
      .filter((line) => /^version:/.test(line));
    const match =
      fields.length === 1 &&
      /^version:[ \t]*(["'])([^"']+)\1[ \t]*(?:#.*)?$/.exec(fields[0]);
    if (match && SEMVER.test(match[2])) return match[2];
  }
  return /^#.*?(\d+\.\d+\.\d+)/m.exec(raw)?.[1] ?? fallback;
}
