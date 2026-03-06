# LSP Troubleshooting Guide (Windows / Claude Code)

## Environment

- **OS**: Windows 11, **Shell**: Git Bash (MSYS2), **Node manager**: mise

### Platform Requirement — mise only

Claude Code uses `uv_spawn` to launch LSP servers, which requires a real `.exe`. Only **mise** creates proper `.exe` shims on Windows. npm global (`.cmd`) and Volta (bash shims) do not work.

---

# Part 1 — TypeScript LSP

## Root Causes

### Bug 1 — `rootUri: null`

Claude Code sends `rootUri: null` in the LSP `initialize` request. Without a workspace root, `typescript-language-server` cannot locate `tsconfig.json` or `node_modules/typescript` and exits immediately:

```
Could not find a valid TypeScript installation. Exiting.
```

### Bug 2 — No `textDocument/didOpen`

Claude Code only opens the single queried file. Cross-file operations (`findReferences`, `goToDefinition`) return empty results without all workspace files indexed.

### TypeScript co-location in mise

When `rootUri` is null, the server looks for TypeScript in its own `node_modules/` as a fallback. Re-install TypeScript alongside the server to enable this fallback:

```bash
npm install --prefix "C:\Users\thatt\AppData\Local\mise\installs\npm-typescript-language-server\5.1.3" typescript typescript-language-server
```

> Always include both packages — installing only `typescript` wipes `typescript-language-server` from that `node_modules`.

---

## Workaround — Proxy (`cli.mjs`)

Replace `cli.mjs` with a proxy that injects `rootUri` and pre-opens all workspace files.

**Location**:
```
C:\Users\thatt\AppData\Local\mise\installs\npm-typescript-language-server\5.1.3\node_modules\typescript-language-server\lib\cli.mjs
```

**Setup**:
```bash
# 1. Backup original
mv ".../lib/cli.mjs" ".../lib/cli.original.mjs"

# 2. Write proxy (see code below), then validate
node --check ".../lib/cli.mjs"
```

**Proxy code**:

```js
#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { readdirSync, readFileSync, statSync } from 'node:fs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const realCli = join(__dirname, 'cli.original.mjs');
const cwd = process.cwd();
const rootUri = 'file:///' + cwd.replace(/\\/g, '/').replace(/ /g, '%20');

const IGNORE = new Set(['node_modules', '.next', '.git', 'dist', 'build', '.turbo', 'out']);

function getAllTsFiles(dir) {
  const results = [];
  for (const entry of readdirSync(dir)) {
    if (IGNORE.has(entry)) continue;
    const full = join(dir, entry);
    try {
      if (statSync(full).isDirectory()) results.push(...getAllTsFiles(full));
      else if (/\.(ts|tsx)$/.test(entry)) results.push(full);
    } catch { }
  }
  return results;
}

const server = spawn(process.execPath, [realCli, ...process.argv.slice(2)], {
  env: process.env,
  windowsHide: true,
  stdio: ['pipe', 'pipe', 'inherit'],
});

server.stdout.pipe(process.stdout);

function sendToServer(msg) {
  const out = JSON.stringify(msg);
  server.stdin.write(`Content-Length: ${Buffer.byteLength(out, 'utf8')}\r\n\r\n${out}`);
}

function preOpenAllFiles() {
  for (const file of getAllTsFiles(cwd)) {
    try {
      const text = readFileSync(file, 'utf8');
      const uri = 'file:///' + file.replace(/\\/g, '/').replace(/ /g, '%20');
      const languageId = file.endsWith('.tsx') ? 'typescriptreact' : 'typescript';
      sendToServer({
        jsonrpc: '2.0',
        method: 'textDocument/didOpen',
        params: { textDocument: { uri, languageId, version: 1, text } },
      });
    } catch { }
  }
}

let buf = Buffer.alloc(0);
process.stdin.on('data', chunk => {
  buf = Buffer.concat([buf, chunk]);
  while (true) {
    const sep = buf.indexOf('\r\n\r\n');
    if (sep === -1) break;
    const header = buf.slice(0, sep).toString('ascii');
    const m = header.match(/Content-Length:\s*(\d+)/i);
    if (!m) { buf = buf.slice(sep + 4); continue; }
    const contentLength = parseInt(m[1]);
    const bodyStart = sep + 4;
    if (buf.length < bodyStart + contentLength) break;
    const body = buf.slice(bodyStart, bodyStart + contentLength).toString('utf8');
    buf = buf.slice(bodyStart + contentLength);
    let msg;
    try { msg = JSON.parse(body); } catch { continue; }
    if (msg.method === 'initialize' && msg.params && !msg.params.rootUri) {
      msg.params.rootUri = rootUri;
      msg.params.rootPath = cwd;
    }
    sendToServer(msg);
    if (msg.method === 'initialized') preOpenAllFiles();
  }
});

process.stdin.on('end', () => server.stdin.end());
server.on('exit', code => process.exit(code ?? 0));
server.on('error', e => { process.stderr.write('proxy error: ' + e.message + '\n'); process.exit(1); });
```

---

## Checklist for mise Updates (TypeScript)

When `typescript-language-server` is updated via mise, the proxy and co-located TypeScript are wiped. Re-apply:

```bash
# 1. Re-install TypeScript alongside typescript-language-server
npm install --prefix "C:\Users\thatt\AppData\Local\mise\installs\npm-typescript-language-server\<VERSION>" typescript typescript-language-server

# 2. Backup original
mv ".../lib/cli.mjs" ".../lib/cli.original.mjs"

# 3. Write proxy as cli.mjs (see code above), then validate
node --check ".../lib/cli.mjs"
```

---

# Part 2 — Python / Pyright LSP

## Root Causes

### Bug 1 — Plugin `lspServers` config not loaded

The `pyright-lsp` plugin's `lspServers` config is inside the marketplace directory and is never read by Claude Code. Result: `pyright-langserver` is never spawned — all LSP operations silently return `[]`.

**Fix**: Add `lspServers` directly to `~/.claude/settings.json`.

### Bug 2 — Malformed `rootUri` and `workspaceFolders`

Claude Code sends:
```
rootUri: "file://C:\Users\thatt\Documents\Coding Project\Science Projects\AI Crop Land-Used"
```

Three problems:
1. `file://` (2 slashes) instead of `file:///` (3 slashes)
2. Backslashes instead of forward slashes
3. Spaces not percent-encoded (should be `%20`)

Pyright cannot find `pyrightconfig.json` → falls back to default settings → `extraPaths` not applied → cross-file imports fail. `workspaceFolders` has the same malformed URI and is read preferentially, so fixing only `rootUri` is insufficient.

**Fix**: Proxy overrides both fields using `pathToFileURL()`.

### Bug 3 — No `textDocument/didOpen`

Same as TypeScript: Claude Code sends `initialized` but no `didOpen` for workspace files. Pyright has nothing in memory → `hover`, `goToDefinition`, `findReferences` all return empty.

**Fix**: Proxy sends `textDocument/didOpen` for all `.py` files after `initialized`.

---

## Setup — Files to Configure

### 1. `~/.claude/settings.json`

Add the `lspServers` block so Claude Code spawns `pyright-langserver`:

```json
{
  "enabledPlugins": { "...": true },
  "lspServers": {
    "pyright": {
      "command": "pyright-langserver",
      "args": ["--stdio"],
      "extensionToLanguage": {
        ".py": "python",
        ".pyi": "python"
      }
    }
  }
}
```

### 2. `pyrightconfig.json` (project root)

```json
{
  "include": ["src"],
  "pythonVersion": "3.12",
  "venvPath": "c:\\Users\\thatt\\Documents\\Coding Project\\Science Projects\\AI Crop Land-Used",
  "venv": ".venv",
  "extraPaths": ["c:\\Users\\thatt\\Documents\\Coding Project\\Science Projects\\AI Crop Land-Used\\src"],
  "stubPath": "c:\\Users\\thatt\\.vscode\\extensions\\ms-python.vscode-pylance-2026.1.1\\dist\\bundled\\stubs"
}
```

Notes:
- `venvPath` = parent directory of the venv folder; `venv` = the folder name (must be split)
- `extraPaths` must be **absolute** — relative paths do not resolve correctly when `rootUri` is malformed
- `stubPath` points to Pylance's bundled stubs for richer pandas/sklearn/matplotlib types; update when Pylance is updated

### 3. Proxy — `langserver.index.js`

**Location**:
```
C:\Users\thatt\AppData\Local\mise\installs\npm-pyright\1.1.408\node_modules\pyright\langserver.index.js
```

**Setup**:
```bash
# 1. Backup original
cp ".../node_modules/pyright/langserver.index.js" \
   ".../node_modules/pyright/langserver.index.original.js"

# 2. Write proxy (see code below), then validate
node --check ".../node_modules/pyright/langserver.index.js"
```

> **Warning**: Always validate with `node --check` after writing. If the proxy is written via bash heredoc or string concatenation, regex escape sequences (`\s`, `\d`) can be corrupted silently — this causes the proxy to drop all LSP messages, making the server appear hung.

**Proxy code**:

```js
#!/usr/bin/env node
'use strict';
// LSP proxy for Pyright -- fixes Claude Code bugs on Windows:
//   Bug 1: malformed/null rootUri -> injected from process.cwd()
//   Bug 2: no textDocument/didOpen -> pre-open all .py files

const { spawn } = require('child_process');
const { join, resolve } = require('path');
const { readdirSync, readFileSync, statSync, appendFileSync } = require('fs');
const { pathToFileURL } = require('url');

const LOG = 'c:/Users/thatt/pyright-proxy.log';
const NL = String.fromCharCode(10);
function log(msg) { try { appendFileSync(LOG, new Date().toISOString() + ' ' + msg + NL); } catch {} }
log('proxy started cwd=' + process.cwd());

const realServer = join(__dirname, 'langserver.index.original.js');
const cwd = resolve(process.cwd());
const rootUri = pathToFileURL(cwd).href;
const SEP = Buffer.from([0x0d, 0x0a, 0x0d, 0x0a]);
const CRLF = Buffer.from([0x0d, 0x0a]);

const IGNORE = new Set(['__pycache__', '.venv', 'venv', '.git', 'node_modules', '.mypy_cache', '.pytest_cache', 'dist', 'build']);

function getAllPyFiles(dir) {
  const results = [];
  let entries;
  try { entries = readdirSync(dir); } catch { return results; }
  for (const entry of entries) {
    if (IGNORE.has(entry)) continue;
    const full = join(dir, entry);
    try {
      const stat = statSync(full);
      if (stat.isDirectory()) results.push(...getAllPyFiles(full));
      else if (entry.endsWith('.py')) results.push(full);
    } catch {}
  }
  return results;
}

const server = spawn(process.execPath, [realServer, ...process.argv.slice(2)], {
  env: process.env, windowsHide: true, stdio: ['pipe', 'pipe', 'inherit'],
});
server.stdout.pipe(process.stdout);

function sendToServer(msg) {
  const body = Buffer.from(JSON.stringify(msg), 'utf8');
  const header = Buffer.from('Content-Length: ' + body.length, 'ascii');
  server.stdin.write(Buffer.concat([header, CRLF, CRLF, body]));
}

function preOpenAllFiles() {
  const files = getAllPyFiles(cwd);
  log('preOpenAllFiles: ' + files.length + ' .py files');
  for (const file of files) {
    try {
      const text = readFileSync(file, 'utf8');
      const uri = pathToFileURL(file).href;
      sendToServer({ jsonrpc: '2.0', method: 'textDocument/didOpen', params: { textDocument: { uri, languageId: 'python', version: 1, text } } });
    } catch {}
  }
}

let buf = Buffer.alloc(0);
process.stdin.on('data', chunk => {
  buf = Buffer.concat([buf, chunk]);
  while (true) {
    const sep = buf.indexOf(SEP);
    if (sep === -1) break;
    const hdr = buf.slice(0, sep).toString('ascii');
    const m = hdr.match(/Content-Length:\s*(\d+)/i);
    if (!m) { buf = buf.slice(sep + 4); continue; }
    const cl = parseInt(m[1], 10);
    const start = sep + 4;
    if (buf.length < start + cl) break;
    const body = buf.slice(start, start + cl).toString('utf8');
    buf = buf.slice(start + cl);
    let msg;
    try { msg = JSON.parse(body); } catch { continue; }
    log('recv ' + msg.method + (msg.id ? ' id=' + msg.id : ''));
    if (msg.method === 'initialize') {
      log('initialize rootUri(before)=' + (msg.params && msg.params.rootUri));
      if (msg.params) {
        msg.params.rootUri = rootUri;
        msg.params.rootPath = cwd;
        msg.params.workspaceFolders = [{ uri: rootUri, name: 'workspace' }];
      }
      log('initialize rootUri(after)=' + rootUri);
    }
    sendToServer(msg);
    if (msg.method === 'initialized') preOpenAllFiles();
  }
});
process.stdin.on('end', () => server.stdin.end());
server.on('exit', code => { log('server exit ' + code); process.exit(code ?? 0); });
server.on('error', e => { process.stderr.write('proxy error: ' + e.message); process.exit(1); });
```

---

## Diagnostic Symptoms

| Symptom | Meaning |
|---|---|
| LSP operations return `[]` instantly | Server not spawned — `lspServers` not in `settings.json` |
| LSP operation hangs forever | Proxy running but `initialize` never forwarded (broken regex in proxy) |
| `"server is starting"` error | Proxy started but `initialize` handshake not complete |
| `"server is running"` error | Server died; Claude Code in exponential backoff — restart Claude Code |
| `goToDefinition` returns "No definition found" | Server running but `pyrightconfig.json` not found (malformed `rootUri`) |
| `hover` returns `Unknown` type | Import not resolved — `extraPaths` not applied |

> Every time the pyright process is killed externally, Claude Code enters a long exponential backoff. The only reliable reset is to restart Claude Code (close + reopen).

---

## Checklist for mise Updates (Pyright)

When `pyright` is updated via mise, the proxy is wiped. Re-apply:

```bash
# 1. Find new version path
ls ~/.local/share/mise/installs/npm-pyright/

# 2. Backup original
cp ".../node_modules/pyright/langserver.index.js" \
   ".../node_modules/pyright/langserver.index.original.js"

# 3. Write proxy as langserver.index.js (see code above), then validate
node --check ".../node_modules/pyright/langserver.index.js"

# 4. Update pyrightconfig.json stubPath if Pylance was updated
# 5. Update venvPath/extraPaths if project was moved
```

Also update `lspServers` in `~/.claude/settings.json` if the `pyright-langserver` command path changes.
