# drive +version-history


List historical version snapshots of a specified file. This shortcut supports both `--as user` and `--as bot`; for automation scenarios, `--as bot` is recommended.

<a id="命令"></a>
## Command

```bash
lark-cli drive +version-history \
  --file-token boxcnxxxxxxxx \
  --as bot

lark-cli drive +version-history \
  --file-token boxcnxxxxxxxx \
  --as user

lark-cli drive +version-history \
  --file-token boxcnxxxxxxxx \
  --limit 50 \
  --cursor 1777013761763 \
  --as bot

lark-cli drive +version-history \
  --file-token boxcnxxxxxxxx \
  --dry-run \
  --as bot
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Yes | Target file token |
| `--limit` | No | Maximum number of entries to return, range `1-200`, default `20` |
| `--cursor` | No | Pagination cursor; fill in with the `next_cursor` returned by the previous page |

<a id="关键行为"></a>
## Key Behaviors

- The shortcut internally always passes `only_tag=true`
- When `has_more=true` is returned, use `next_cursor` to continue paginating
- `versions[].version` is the long numeric version string passed to `drive +version-get` / `+version-revert` / `+version-delete`; `tag` is only a display sequence number and cannot replace `version`
- `versions[].is_deleted` is a boolean value indicating whether that historical version has been deleted

<a id="返回值"></a>
## Return Value

```json
{
  "ok": true,
  "identity": "bot",
  "data": {
    "versions": [
      {
        "version": "7633658129540910621",
        "name": "report.md",
        "edited_at": "1777013761763",
        "edited_by": "ou_xxx",
        "size_bytes": "12345",
        "action_type": "upload",
        "is_deleted": false,
        "tag": 7
      }
    ],
    "has_more": true,
    "next_cursor": "1777013761763"
  }
}
```

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- All commands for cloud space (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) -- Authentication and global parameters
