<a id="apps-openapi-key-命令族-sop"></a>
# apps openapi-key command family SOP

Manage the HTTP API Keys exposed externally by Miaoda apps (`/openapi/**` authentication credentials). All operations require `--as user` (AuthType: user). `--help` is the complete source for parameter details; this file only records the domain rules that an Agent will get wrong if it does not read them.

<a id="命令路由"></a>
## Command routing

| Command | Purpose |
|---|---|
| `+openapi-key-list` | List all API Keys of the app (masked) |
| `+openapi-key-get` | View details of a single Key (masked) |
| `+openapi-key-create` | Create a new Key, **the raw secret is visible only once** |
| `+openapi-key-update` | Rename or change config (does not change status) |
| `+openapi-key-enable` | Enable Key (status→1) |
| `+openapi-key-disable` | Disable Key (status→0), **for leaks/suspected leaks prefer this over delete** |
| `+openapi-key-delete` | Permanently delete Key (irreversible) |
| `+openapi-key-reset` | Rotate the secret (refresh the raw Key), **visible only once** |

<a id="脱敏口径安全关键"></a>
## Masking rules (security-critical)

- `list` / `get` / `update` / `enable` / `disable`: the returned structure has **no** `api_key` field, only `key_preview` (format: `****` + last 4 characters of the raw secret, e.g. `****5f4a`).
- `create` / `reset`: the raw secret is returned **only** once in `data.api_key` (top level); at the same time a one-time notice is printed to stderr:
  ```
  warning: this api_key is shown only once and is NOT stored by lark-cli — copy it now and store it in your own secret manager.
  ```
- The raw secret is never written to cache / config / recent / debug log / error messages.

<a id="一次性密钥语义"></a>
## One-time secret semantics

The CLI does not save the raw secret. The secret is returned only once with the response at `create` / `reset`. **A lost secret cannot be recovered with `get`**—the only way to recover is `+openapi-key-reset` to regenerate a new secret (the old secret is invalidated at the same time).

<a id="scope-结构与-cli-表达"></a>
## scope structure and CLI expression

The real structure of the backend `config.request_scope` (**snake_case**—stipulated by the Lark Open Gateway `/open-apis/` external contract; the camelCase go.tag of `api_key.thrift` is an internal representation, and OGW has already converted it to snake_case):

```json
{
  "allow_all": true,
  "http_infos": [
    { "http_method": "GET", "http_path": "/openapi/some-path" }
  ]
}
```

- `allow_all=true`: open all `/openapi/**` routes of the app; `http_infos` is ignored in this case.
- `allow_all=false`: authorize route by route according to `http_infos`; each entry requires `http_method` (uppercase) + `http_path` (starting with `/openapi/`).

The CLI provides three mutually exclusive ways to express scope:

| flag | Purpose | Notes |
|---|---|---|
| `--scope-all` | `allow_all=true`, open all routes | bool flag; explicitly passing `--scope-all=false` also counts as "set" |
| `--scope-api 'METHOD /openapi/path'` | Authorize one route at a time, repeatable | Routes are taken from the app's `docs/openapi.json` |
| `--scope '<raw request_scope JSON>'` | Advanced escape hatch, directly passes request_scope JSON (snake_case) | The CLI only validates that it is legal JSON; `--scope` is mutually exclusive with `--scope-all`/`--scope-api` |

<a id="scope-值来源"></a>
### Where scope values come from

The `/openapi/**` route definitions of a Miaoda app are defined in the app repository and are also kept in sync in `docs/openapi.json` (each `"/openapi/..."` entry under `paths` + HTTP method). To decide which routes to authorize, read the target app's own `docs/openapi.json` and take the `(method, path)` pairs. The CLI itself does not provide API route discovery (planned for P1).

<a id="高风险操作"></a>
## High-risk operations

`delete` and `reset` are high-risk (`high-risk-write`) and have the following constraints:

- `--yes` must be passed explicitly (framework `cmdutil.RequireConfirmation`); when missing, the exit code is 10, **do not automatically add `--yes`** (follow the lark-shared security red line).
- Supports `--dry-run` to view the HTTP request that will be executed (excluding the secret); when unsure, dry-run first.
- **Leak scenario**: prefer `+openapi-key-disable` to disable immediately, rather than `+openapi-key-delete`—disabling can be restored at any time with enable, while delete is irreversible.

<a id="典型决策场景"></a>
## Typical decision scenarios

| User intent | Correct operation |
|---|---|
| "The key leaked, disable it first" | `+openapi-key-disable` (not delete) |
| "I lost/forgot the key, give me another one" | `+openapi-key-reset` (not create a new key; reset rotates the secret and keeps the original key config) |
| "What is my key's secret" | Explain: list/get do not echo the raw secret; you can only rotate with `+openapi-key-reset` |
| "Create a key with permission restrictions for the app" | `+openapi-key-create --name ... --scope-api 'GET /openapi/...'` (routes are taken from the app's `docs/openapi.json`) |

<a id="不在本模块-范围"></a>
## Out of scope for this module

- Full OpenAPI spec export, real-time log tail, Webhook consumption, multiple authentication methods: not supported in this release.
- Identity selection, handling insufficient permissions (`missing_scopes`→`console_url`), exit-10 approval, general framework for high-risk operations: see [`../../shared/index.md`](../../shared/index.md), not repeated here.
