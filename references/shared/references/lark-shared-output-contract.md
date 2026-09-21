# JSON output contract

With `--format json` (the default), success and error envelopes differ.

Success is written to stdout with exit code 0:

```json
{"ok": true, "identity": "user", "data": {"guid": "..."}, "meta": {"count": 1}}
```

Errors are written to stderr with a nonzero exit code:

```json
{"ok": false, "identity": "user", "error": {"type": "authorization", "subtype": "missing_scope", "code": 99991679, "message": "...", "hint": "...", "missing_scopes": ["..."]}}
```

Use `ok == true` together with process status, not top-level `code == 0`. Successful CLI envelopes have no top-level `code` or `msg`. `error.code` is the upstream numeric OpenAPI code, not the CLI success indicator.

Testing for the old raw-API shape `{"code":0,"msg":"ok"}` misclassifies successful wrapped commands. In a write wrapper this can cause duplicate creation by retrying an operation that already succeeded. If success is uncertain, inspect state before resubmitting.
