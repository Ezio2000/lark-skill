# OpenAPI discovery

Use when neither a module shortcut nor a registered CLI API covers the requested operation. Check the relevant service's `--help` first; use an existing command when available.

## Discover the contract

Fetch official documentation with the available web-reading tool. Follow actual links rather than guessing endpoints:

1. Brand index: [Feishu](https://open.feishu.cn/llms.txt) or [Lark](https://open.larksuite.com/llms.txt), matching the user's account/resource domain.
2. Relevant module index (`llms-<module>.txt`).
3. The operation's complete API page.

Extract HTTP method, path, path/query parameters, body fields and types, required identity/scopes, response structure, pagination, rate limits, and errors. Reuse a known official operation page directly when already available. Documentation may be Chinese; interpret it and respond in the user's language.

## Execute

Use the documented contract with explicit identity:

```sh
lark-cli api GET /open-apis/<documented-path> --params '{"key":"value"}' --as user
lark-cli api POST /open-apis/<documented-path> --data '{"key":"value"}' --as user
```

Select the actual HTTP method from the documentation; do not infer it from the task name. Use bot identity only for the selected application workflow. Inspect `lark-cli api --help` if required CLI options are unknown.

The user's specific request authorizes its corresponding mutation; discovery or an explanation request does not. Resolve ambiguous targets or newly introduced effects before writing. Parse the CLI output contract and query state before retrying an uncertain write.

For an API explanation, provide its purpose, method/path, required parameters, scopes, a complete invocation, and relevant constraints. For an execution request, perform the authorized operation and report the result without forcing a documentation report.

- [Authentication](../shared/index.md): only for setup or actual auth/scope errors.
- [Extend this skill](../skill-maker/index.md): capture a proven recurring operation as a reference.
