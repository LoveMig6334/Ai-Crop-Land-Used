# Claude Code LSP Troubleshooting on Windows

## Summary

Claude Code's LSP tool has two bugs on Windows that prevent TypeScript intelligence from working. This document records the full debugging journey, the root causes found, the workaround applied, and a draft bug report.

---

## Environment

- **OS**: Windows 11
- **Shell**: Git Bash (MSYS2)
- **Node manager**: mise
- **Project**: Next.js 15, TypeScript 5.9.3
- **LSP server**: `typescript-language-server` v5.1.3
- **Claude Code model**: claude-sonnet-4-6

---

## Root Causes

### Bug 1 — Claude Code passes `rootUri: null` on LSP initialize

When Claude Code's LSP tool spawns `typescript-language-server`, it sends an LSP `initialize` request with `rootUri: null`. Without a workspace root, the server cannot locate:

- The project's `tsconfig.json`
- The project's `node_modules/typescript`

This causes the server to exit immediately with:

```
Request initialize failed with message: Could not find a valid TypeScript installation.
Please ensure that the "typescript" dependency is installed in the workspace
or that a valid `tsserver.path` is specified. Exiting.
```

**Verified with a manual LSP initialize test:**

```js
// rootUri: null → server crashes
params: { rootUri: null, ... }
// → error: "Could not find a valid TypeScript installation"

// rootUri: correct path → server works
params: { rootUri: 'file:///C:/Users/.../cdsc', ... }
// → success, finds TypeScript 5.9.3 from workspace node_modules
```

**Expected behavior**: Claude Code should derive `rootUri` from the `filePath` parameter passed to the LSP tool by walking up to find `package.json` or `tsconfig.json`.

---

### Bug 2 — Claude Code does not pre-open workspace files

Even after fixing `rootUri`, only the single file passed to the LSP tool is opened via `textDocument/didOpen`. The TypeScript server needs all project files opened (or a valid `tsconfig.json` traversal) to answer cross-file queries like `findReferences` and `goToDefinition`.

**Symptom**: `workspaceSymbol` returned only 24 symbols from `lib/types.ts` instead of 651 symbols from the full workspace.

**Expected behavior**: After sending `initialized`, Claude Code should send `textDocument/didOpen` for all relevant workspace files, or rely on the server's `tsconfig.json`-based discovery (which requires `rootUri`).

---

## Platform Issue — Windows Binary Resolution

### Why `uv_spawn` fails with npm/Volta shims

Claude Code uses Node.js's `child_process.spawn` (libuv `uv_spawn`) to launch the LSP server. On Windows, this requires a real `.exe` file. Package managers that install only `.cmd` or bash script shims do not work:

| Package manager | Binary type | Works with `uv_spawn`? |
|---|---|---|
| npm global | `.cmd` batch file | No |
| Volta | bash script shim | No |
| mise | `.exe` shim | Yes |

**mise** is the only tested package manager on Windows that creates proper `.exe` shims compatible with Claude Code's LSP spawning mechanism.

---

## Debugging Timeline

### Session 1 — npm global install

```
Error: ENOENT: no such file or directory, uv_spawn 'typescript-language-server'
```

`typescript-language-server` was installed via npm, which creates `.cmd` files. `uv_spawn` cannot execute `.cmd` files without `shell: true`.

**Action**: Switched to Volta.

---

### Session 2 — Volta

```
Error: ENOENT: no such file or directory, uv_spawn 'typescript-language-server'
```

Volta creates bash script shims (not `.exe`) when configured via Git Bash on Windows. Volta also was not itself on the PATH, making the shims non-functional.

**Action**: Switched to mise.

---

### Session 3 — mise (first attempt)

mise creates proper `.exe` shims. The binary was found. New error:

```
Request initialize failed with message: Could not find a valid TypeScript installation.
```

This confirmed **Bug 1** — `rootUri: null`. TypeScript IS installed in the project (`node_modules/typescript/lib/tsserver.js`), but the server cannot find it without `rootUri`.

---

### Session 4 — TypeScript co-location in mise

The mise installation for `typescript-language-server` lives at:

```
C:\Users\thatt\AppData\Local\mise\installs\npm-typescript-language-server\5.1.3\
```

This is a **separate** directory from the mise Node.js installation:

```
C:\Users\thatt\AppData\Local\mise\installs\node\24.14.0\
```

When `rootUri` is null, `typescript-language-server` looks for TypeScript in its own `node_modules/` as a fallback. Installing TypeScript globally (`npm install -g typescript` or `mise install npm:typescript`) puts it in a different tree — not accessible as a fallback.

**Fix**: Install TypeScript directly into the typescript-language-server's mise `node_modules`:

```bash
npm install --prefix "C:\Users\thatt\AppData\Local\mise\installs\npm-typescript-language-server\5.1.3" typescript typescript-language-server
```

> **Note**: Running this with just `typescript` (not both packages) wipes `typescript-language-server` from `node_modules`. Always include both.

**Result**: Server initializes without crashing. But `findReferences` and cross-file operations still returned no results (Bug 2).

---

### Session 5 — LSP Proxy (workaround for both bugs)

Since Claude Code cannot be modified directly, a stdio proxy was created by wrapping `cli.mjs` (the typescript-language-server entry point).

**How it works**:

1. Renames `cli.mjs` → `cli.original.mjs`
2. Installs a new `cli.mjs` that:
   - Intercepts the LSP `initialize` request from Claude Code
   - Injects `rootUri` derived from `process.cwd()`
   - Forwards the modified request to `cli.original.mjs` (the real server)
   - After `initialized`, sends `textDocument/didOpen` for all `.ts`/`.tsx` files in the workspace
   - Pipes all other messages through unchanged

**Proxy location**:
```
C:\Users\thatt\AppData\Local\mise\installs\npm-typescript-language-server\5.1.3\node_modules\typescript-language-server\lib\cli.mjs
```

**Original server**:
```
...lib\cli.original.mjs
```

**Final proxy code** (`cli.mjs`):

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

### Final LSP Capability Results (after workaround)

| Operation | Result |
|---|---|
| `hover` | Fully working — returns type info |
| `documentSymbol` | Fully working — lists all symbols in file |
| `workspaceSymbol` | Fully working — 651 symbols across workspace |
| `findReferences` | Fully working — 9 references across 5 files |
| `goToDefinition` | Fully working |
| `goToImplementation` | Working (no impl for interfaces, expected) |
| `prepareCallHierarchy` | Working (N/A for type declarations) |

---

## Additional Finding — TypeScript Diagnostics

Once the LSP was fully operational, the system automatically surfaced TypeScript diagnostics:

```
app/admin/(protected)/events/EventsManager.tsx:63  — 'FormEvent' is deprecated [6385]
app/admin/login/page.tsx:16                        — 'FormEvent' is deprecated [6385]
app/components/ApplicationForm.tsx:41              — 'FormEvent' is deprecated [6385]
```

---

## Bug Report Draft

**Title**: LSP tool passes `rootUri: null` on Windows, preventing TypeScript Language Server from initializing

**Affected**: Claude Code on Windows (all versions tested)

**Steps to reproduce**:
1. Install `typescript-language-server` and ensure it is accessible as an `.exe` via mise
2. Open a TypeScript project in Claude Code
3. Use any LSP operation (hover, findReferences, etc.)
4. Observe the error or empty results

**Root cause**:
The LSP tool calls `typescript-language-server --stdio` and sends an LSP `initialize` request with `rootUri: null`. The TypeScript Language Server requires `rootUri` to locate the project's TypeScript installation and `tsconfig.json`. Without it, the server exits immediately.

**Expected behavior**:
Claude Code should derive `rootUri` from the `filePath` argument passed to the LSP tool by walking up the directory tree to find a `package.json` or `tsconfig.json`.

**Secondary issue**:
Even with a valid `rootUri`, Claude Code only sends `textDocument/didOpen` for the single queried file. Cross-file operations (`findReferences`, `goToDefinition`) require the server to have indexed the full workspace. Claude Code should either send `didOpen` for all workspace files after `initialized`, or rely on the server's own tsconfig-based discovery.

**Platform note**:
On Windows, `uv_spawn` cannot execute `.cmd` or bash script shims. The LSP binary must be a real `.exe`. Only mise (among npm, Volta, mise) produces compatible `.exe` shims on Windows.

**Workaround**:
A stdio proxy (`cli.mjs`) wraps the real server entry point to inject `rootUri` and pre-open all workspace files. See proxy code above.

**Report here**: https://github.com/anthropics/claude-code/issues

---

## Checklist for Future mise Updates

When `typescript-language-server` is updated via mise, the proxy and co-located TypeScript will be wiped. Re-apply:

```bash
# 1. Re-install TypeScript alongside typescript-language-server
npm install --prefix "C:\Users\thatt\AppData\Local\mise\installs\npm-typescript-language-server\<VERSION>" typescript typescript-language-server

# 2. Rename original entry point
mv ".../lib/cli.mjs" ".../lib/cli.original.mjs"

# 3. Place the proxy as the new cli.mjs (see proxy code above)
```
