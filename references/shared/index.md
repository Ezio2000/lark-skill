# Authentication and diagnostics

Ordinary business requests reuse the existing login and identity. Shared execution rules are in the [entrypoint](../../SKILL.md). Read only the reference matching the actual issue.

| Issue | Reference |
|---|---|
| Login/logout, user/bot identity, scopes, missing_scopes, authorization, or console_url | [Identity and permissions](references/lark-shared-identity-and-permissions.md) |
| JSON envelopes, stdout/stderr, wrappers, or success detection | [Output contract](references/lark-shared-output-contract.md) |
| Exit 10, confirmation_required, flags, or retry authorization | [Confirmation flags](references/lark-shared-high-risk-approval.md) |
| Initial application configuration, or an explicit config init --new requirement | [Configuration initialization](references/lark-shared-config-init.md) |
| CLI/skill upgrades, deprecated commands, or _notice | [Updates](references/lark-shared-update-notice.md) |
| Resolve a Wiki node to its underlying resource | [Wiki token routing](references/lark-wiki-token-routing.md) |

When an authorization/configuration command returns a verification or console URL, preserve it verbatim. Generate and display a PNG QR code with `lark-cli auth qrcode`; use ASCII only if requested. Do not re-encode or reconstruct the query string.

Recover authorization only for an actual expired login or missing permissions needed for the task. Follow the user's requested scope. Platform permission restrictions are determined by actual responses, not inferred from an empty result.
