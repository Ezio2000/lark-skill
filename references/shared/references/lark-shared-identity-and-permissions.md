# Identity and permissions

## Authentication routing

| Intent | Command / behavior |
|---|---|
| Explicitly request all scopes | `lark-cli auth login --domain all --no-wait --json` |
| Authorize selected domains | `lark-cli auth login --domain docs --domain drive --no-wait --json`; domains can repeat or be comma-separated |
| Authorize a specific scope | `lark-cli auth login --scope "<scope>" --no-wait --json` |
| Verify login/token and identify the user | `lark-cli auth status --json --verify` |
| Inspect effective identity quickly | `lark-cli whoami` |
| Log the user out locally | `lark-cli auth logout --json`; check `loggedOut:true` |
| Missing bot scopes | Configure scopes in the developer console, using the returned `console_url`; user login cannot grant bot scopes |
| Revoke server-side app authorization | The user must use Lark authorization management; local logout does not revoke it |
| Revoke one granted scope | The CLI cannot selectively revoke one scope; use authorization management |

For status results, inspect `identity`, `verified`, and `identities.user` fields `status`, `userName`, `openId`, `tokenStatus`, and `scope`. Do not run verification as a routine preflight for every business request.

To suppress informational notices for one machine-parsed command:

```sh
LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1 lark-cli auth status --json --verify
```

## Identity and continuity

| Identity | Selection | Credentials | Typical scope |
|---|---|---|---|
| User | `--as user` | User authorization through `auth login` | The person's resources and permitted actions |
| Application/bot | `--as bot` | Configured app ID/secret | Application-owned or explicitly accessible resources |

Bot identity does not inherit the user's personal visibility or ownership. For example, a bot calendar query may return its own empty calendar; bot-created resources belong to that operator. Some APIs support explicit application access to other resources, subject to their own scope and ACL rules.

Bot scopes are configured in the developer console. User operations need both application scope availability and user authorization. Explicit `--as` takes precedence; omitting it lets the CLI choose from available credentials. Preserve explicit source identity across a workflow, including recovery.

## Permission recovery

Error fields may include `missing_scopes` (alternatives, not necessarily all required), `console_url`, and `hint`. Distinguish missing scope from resource ACL or tenant-policy restrictions.

- Bot: provide the exact developer-console URL and explain the required configuration. Do not run `auth login` to fix bot permissions.
- User: initiate scoped authorization with `--scope`, `--domain`, or `--recommend`. Repeated login grants accumulate; logging in with fewer scopes does not revoke earlier grants.

```sh
lark-cli auth login --domain <domain> --no-wait --json
lark-cli auth login --scope "<missing_scope>" --no-wait --json
```

Restore only the original task after authentication succeeds. An error hint does not authorize additional operations.

## Agent-mediated split flow

1. Start `auth login` with the selected scope/domain and `--no-wait --json`.
2. Capture the returned `verification_url` and `device_code`.
3. Generate a PNG QR code: `lark-cli auth qrcode <verification_url> --output <path>`.
4. Show the original URL and QR code, and tell the user to return after completing authorization. Yield the turn so the link is visible.
5. After the user reports completion, run `lark-cli auth login --device-code <device_code>` yourself to poll and finish login.
6. Resume the authorized business operation once login succeeds.

Do not immediately block on device-code polling after displaying a link in a harness that only reveals the final response; that can prevent the user from seeing the link. Do not ask the user to run the completion command instead of performing it.

Keep the device code only for its current flow. If a new flow is required or the link expires, preserve the intended scope/domain/recommend selection and any `--exclude` values, and request a fresh link with `--no-wait --json`; do not reuse expired links/codes.
