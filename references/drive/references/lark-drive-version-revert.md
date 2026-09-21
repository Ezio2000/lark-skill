# drive +version-revert


Roll back a file to a specified historical version. This shortcut supports both `--as user` and `--as bot`; for automation scenarios, `--as bot` is recommended.

<a id="命令"></a>
## Command

```bash
lark-cli drive +version-revert \
  --file-token boxcnxxxxxxxx \
  --version 7633658129540910621 \
  --as bot

lark-cli drive +version-revert \
  --file-token boxcnxxxxxxxx \
  --version 7633658129540910621 \
  --as user
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Yes | Target file token |
| `--version` | Yes | The long numeric `version` field returned by `drive +version-history`, not `tag` |

<a id="返回值"></a>
## Return Value

No additional business fields; success or failure is determined by the command result.

<a id="参考"></a>
## References

- [lark-drive](../index.md) -- All commands for Drive (cloud drive/cloud storage)
- [lark-shared](../../shared/index.md) -- Authentication and global parameters
