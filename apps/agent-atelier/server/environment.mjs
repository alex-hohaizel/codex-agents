// Worker processes receive runtime paths and locale, never a copy of caller credentials.
const runtimeKeys = [
  "PATH",
  "HOME",
  "USER",
  "LOGNAME",
  "SHELL",
  "TMPDIR",
  "TMP",
  "TEMP",
  "LANG",
  "LC_ALL",
  "LC_CTYPE",
  "TZ",
  "TERM",
  "TERMINFO",
  "TERMINFO_DIRS",
  "COLORTERM",
  "CODEX_HOME",
  "XDG_CONFIG_HOME",
  "XDG_DATA_HOME",
  "XDG_CACHE_HOME",
  "NODE_EXTRA_CA_CERTS",
  "SSL_CERT_FILE",
  "SSL_CERT_DIR",
  "SYSTEMROOT",
  "WINDIR",
  "PATHEXT",
  "COMSPEC",
  "USERPROFILE",
  "APPDATA",
  "LOCALAPPDATA",
  "HOMEDRIVE",
  "HOMEPATH",
  "AGENT_SYSTEM_PYTHON",
  "AGENT_SYSTEM_NODE",
  "PYTHONUTF8",
  "PYTHONIOENCODING",
  "PYTHONDONTWRITEBYTECODE",
];
const proxyKeys = [
  "HTTP_PROXY",
  "HTTPS_PROXY",
  "ALL_PROXY",
  "http_proxy",
  "https_proxy",
  "all_proxy",
];
export function runtimeEnvironment(
  source = process.env,
  { service = false } = {},
) {
  const result = {};
  for (const key of runtimeKeys)
    if (typeof source[key] === "string") result[key] = source[key];
  for (const key of proxyKeys)
    if (source[key]) {
      try {
        const url = new URL(source[key]);
        if (!url.username && !url.password) result[key] = source[key];
      } catch {}
    }
  if (source.NO_PROXY) result.NO_PROXY = source.NO_PROXY;
  if (source.no_proxy) result.no_proxy = source.no_proxy;
  if (service)
    for (const key of [
      "ATELIER_DATA_DIR",
      "ATELIER_PORT",
      "ATELIER_DEV_ORIGIN",
    ])
      if (source[key]) result[key] = source[key];
  return result;
}
export function shellEnvironmentConfig(environment) {
  const entries = Object.entries(environment)
    .map(([key, value]) => `${key} = ${JSON.stringify(value)}`)
    .join(", ");
  return [
    "-c",
    'shell_environment_policy.inherit="none"',
    "-c",
    "shell_environment_policy.ignore_default_excludes=false",
    "-c",
    `shell_environment_policy.set={ ${entries} }`,
  ];
}
