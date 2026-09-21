
# mail +watch


Listen for new mail events in real time (`mail.user_mailbox.event.message_received_v1`).

**Permission requirements:** The app needs the `mail:event` and `mail:user_mailbox.message:readonly` permissions, as well as the field permissions `mail:user_mailbox.message.address:read`, `mail:user_mailbox.message.subject:read`, and `mail:user_mailbox.message.body:read`, and the bot must subscribe to the event `mail.user_mailbox.event.message_received_v1`. On-demand permissions (you will be prompted to apply when missing): using `--folders` / `--folder-ids` to filter custom folders requires `mail:user_mailbox.folder:read`; using `--labels` / `--label-ids` to filter custom labels requires `mail:user_mailbox.message:modify`.

<a id="命令"></a>
## Command

```bash
# Default: table output of message metadata
lark-cli mail +watch

# Output only message data (jq-friendly)
lark-cli mail +watch --msg-format metadata --format data

# Output condensed metadata (message_id / thread_id / folder_id / label_ids / internal_date / message_state)
lark-cli mail +watch --msg-format minimal --format data

# Output full plain text body
lark-cli mail +watch --msg-format plain_text_full --format data

# Output the complete message (including body-related fields)
lark-cli mail +watch --msg-format full --format data

# Output the raw event body
lark-cli mail +watch --msg-format event --format data

# Listen to the specified mailbox
lark-cli mail +watch --mailbox alice@company.com

# Filter by folder/label (client-side filtering, supports name or ID)
lark-cli mail +watch --folders '["收件箱项目"]' --label-ids '["FLAGGED"]'

# Write to file
lark-cli mail +watch --msg-format metadata --output-dir ./mail-events

# View the output field descriptions for each --msg-format (run before parsing)
lark-cli mail +watch --print-output-schema
```

<a id="参数"></a>
## Parameters

| Parameter | Default | Description |
|------|------|------|
| `--mailbox <id>` | `me` | Target mailbox to subscribe to |
| `--msg-format <mode>` | `metadata` | Output mode: `metadata` / `minimal` / `plain_text_full` / `full` / `event` |
| `--format <mode>` | `data` | Output style: `json` (NDJSON stream with ok/data envelope) / `data` (bare NDJSON stream) |
| `--folder-ids <json-array>` | — | Folder ID filter, e.g. `["INBOX","SENT"]` |
| `--folders <json-array>` | — | Folder name filter (union with `--folder-ids`) |
| `--label-ids <json-array>` | — | Label ID filter, e.g. `["FLAGGED","IMPORTANT"]` |
| `--labels <json-array>` | — | Label name filter (union with `--label-ids`) |

> **Filter logic:** `--folder-ids`/`--folders` and `--label-ids`/`--labels` are in an **AND** relationship, meaning a message must match **both** the specified folder and label to be output. Within the same category of parameters, the relationship is **OR** (matching any one is sufficient). Newly received mail usually only has system labels (such as `UNREAD`, `IMPORTANT`) and will not automatically carry custom labels.
| `--output-dir <dir>` | — | Write each event to a separate JSON file |
| `--print-output-schema` | — | Print the output field descriptions for each `--msg-format` (run this command before parsing the output) |
| `--dry-run` | — | Only preview the subscription request, without actually connecting |

<a id="--msg-format-输出结构--format-json"></a>
## --msg-format output structure (--format json)

Each event is output as one line of NDJSON.

**`metadata`** (default, suitable for triage/notification)
```json
{"ok":true,"data":{"message":{"message_id":"...","thread_id":"...","subject":"...","head_from":{"name":"Alice","mail_address":"alice@example.com"},"to":[{"name":"Bob","mail_address":"bob@example.com"}],"folder_id":"INBOX","label_ids":["IMPORTANT"],"internal_date":"1742800000000","message_state":1,"body_preview":"Please find attached..."}}}
```

**`minimal`** (IDs and state only, suitable for tracking read/folder changes)
```json
{"ok":true,"data":{"message":{"message_id":"...","thread_id":"...","folder_id":"INBOX","label_ids":["IMPORTANT"],"internal_date":"1742800000000","message_state":1}}}
```

**`plain_text_full`** (all metadata fields + full plain text body)
```json
{"ok":true,"data":{"message":{"message_id":"...","subject":"...","head_from":{...},"folder_id":"INBOX","label_ids":[...],"body_preview":"...","body_plain_text":"<base64url>"}}}
```

**`event`** (raw WebSocket event, no API request made, suitable for debugging)
```json
{"ok":true,"data":{"header":{"event_id":"abc123","event_type":"mail.user_mailbox.event.message_received_v1","create_time":"1742800000000"},"event":{"message_id":"...","mail_address":"user@example.com"}}}
```

**`full`** (all fields, including HTML body and attachments)
```json
{"ok":true,"data":{"message":{"message_id":"...","subject":"...","head_from":{...},"body_preview":"...","body_plain_text":"<base64url>","body_html":"<base64url>","attachments":[{"name":"report.pdf","size":102400}]}}}
```

<a id="参考"></a>
## References

- [lark-mail](../index.md) — Mail domain overview
- [lark-mail-triage](lark-mail-triage.md) — Mail summary list
- [lark-event](../../event/index.md) — General event subscription
