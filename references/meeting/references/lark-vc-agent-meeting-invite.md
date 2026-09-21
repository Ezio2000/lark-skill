# vc +meeting-invite

Invite specified users through the Agent Bot API, or invite eligible Calendar participants with one click.

```bash
lark-cli vc +meeting-invite --as bot --meeting-id 7628568141510692381 --type SELECTED --open-ids ou_xxx,ou_yyy
lark-cli vc +meeting-invite --as bot --meeting-id 7628568141510692381 --type ALL_SUGGESTED
lark-cli vc +meeting-invite --as bot --meeting-id 7628568141510692381 --type ALL_SUGGESTED --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
| --- | --- | --- |
| `--meeting-id` | Yes | Long numeric Meeting ID, not the 9-digit meeting number. |
| `--type` | Yes | `SELECTED` or `ALL_SUGGESTED`, case-insensitive. |
| `--open-ids` | Required when `SELECTED` | User `open_id` (`ou_xxx`), supports comma-separated or repeated passing, up to 200; must not be passed when `ALL_SUGGESTED`. |

This shortcut only supports bot identity, calling `POST /open-apis/vc/v1/bots/invite`.

- `SELECTED` explicitly sends user `open_id`; locally, input with more than 200 IDs is rejected before the request.
- `ALL_SUGGESTED` sends only the invite type. The server resolves the one-click invite candidate set based on Calendar status and applies the 200-person limit.
- Request contract: `SELECTED` sends `invite_type=2`, `invitees=[{"id":"ou_xxx","user_type":1}]`, and the query parameter `user_id_type=open_id`; `ALL_SUGGESTED` sends `invite_type=1` and omits `invitees`.
- Response contract: `SELECTED` can return the `invite_results` of explicitly invited people; the CLI displays each item's `invited` or `failed` status according to the response `id`. `ALL_SUGGESTED` returns only aggregate fields, not per-user `invite_results`.
- The `has_more=true` of `ALL_SUGGESTED` indicates that the candidates exceed the server's single-request limit of 200 people, and is not a pagination signal. This API has no continuation or `page_token`; the CLI displays a truncation notice without outputting `has_more`.

<a id="权限与前置条件"></a>
## Permissions and Prerequisites

- The target must be a Calendar VC meeting, and the app Bot must already be in the meeting.
- Agent Invite depends on the meeting's Agent join capability. If the calendar does not have AI/Agent meeting settings enabled, the invite request will fail.
- `SELECTED` containing only one invitee reuses the regular single-point invite policy, and regular in-meeting participants may also have permission to invite that user.
- `ALL_SUGGESTED` and multi-user `SELECTED` use the batch/suggested-list invite policy. In actual calls, the Bot should be the current host or co-host; a regular participant Bot may not have batch invite permission.
