# apps observability


Query online runtime observability and product access analytics for Miaoda apps. All observability commands support only `--environment online`; when `--environment` is omitted, the default is online, and passing dev or any other environment is not supported. Do not use the old `--env`, and do not use short options.

The user-side environment for logs and traces is still online; however, the backend `app_env` in the OpenAPI request body is always sent as `runtime`, because the runtime logs and traces of online apps are stored in the runtime observability environment. The dry-run output will show this backend parameter.

The `--environment` for metric / analytics is only a CLI-side online-only validation: `+metric-list` and `+analytics-list` will not send `env` or `app_env` to the OpenAPI body. Not seeing an environment field in dry-run is expected behavior; do not fabricate parameters.

Time filtering supports relative time (such as `30s`, `5m`, `0.5h`, `2h`, `3d`, `1w`), local date / time, and RFC3339.

<a id="命令选择"></a>
## Command selection

- Log search: use `+log-list` to search logs, and use `+log-get` to retrieve a single log by log ID.
- `+log-list` no longer supports `--log-id`; when you already have a log ID, use `+log-get --log-id <log_id>` directly.
- Frontend ERROR log details: `+log-get` may supplement `source_stack`; there is no separate source-stack command.
- Trace search: use `+trace-list` to search traces, and use `+trace-get` to retrieve details by trace ID.
- Runtime metrics: use `+metric-list` for request count, errors, latency, CPU, and memory.
- Product analytics: use `+analytics-list` for business access analytics such as PV, UV, and visit volume; do not mix them into runtime metric queries.
- `+analytics-list` sends `metric_types`, nanosecond timestamps, and `need_pack_lack_point=false` according to the latest OpenAPI; `group_by` is not currently supported.
- When the user asks about "API request volume, error volume, latency, slow APIs, or many errors in the last hour," this is platform runtime monitoring, not local project files. First use `apps +list --keyword` to find `app_id`, then query `+metric-list`.

<a id="示例"></a>
## Examples

```bash
lark-cli apps +log-list --app-id <app_id> --level error --keyword timeout --since 0.5h
lark-cli apps +log-get --app-id <app_id> --log-id <log_id>
lark-cli apps +trace-list --app-id <app_id> --trace-id <trace_id>
lark-cli apps +trace-get --app-id <app_id> --trace-id <trace_id>
lark-cli apps +metric-list --app-id <app_id> --metric requests --series total --since 1d
lark-cli apps +metric-list --app-id <app_id> --metric requests --since 1h
lark-cli apps +metric-list --app-id <app_id> --metric latency --since 1h
lark-cli apps +metric-list --app-id <app_id> --metric latency --series p99 --since 1d
lark-cli apps +metric-list --app-id <app_id> --metric cpu --since 1h
lark-cli apps +metric-list --app-id <app_id> --metric memory --since 1h
lark-cli apps +analytics-list --app-id <app_id> --analytics users --series active-users --granularity day
lark-cli apps +analytics-list --app-id <app_id> --analytics page-view --granularity day
```

<a id="使用边界"></a>
## Usage boundaries

- If the user asks about "slow APIs, many errors, or high CPU/memory," prioritize `+metric-list`.
- If `+metric-list --metric requests` is not passed `--series`, it returns both the total request count total and the error count error; if `--metric latency` is not passed `--series`, it returns both p50 and p99. Pass `--series total|error|p50|p99` only when you want to see a single curve.
- Use `--api <path-or-name>` to narrow the scope by API; there is currently no `group-by` parameter, so do not invent one.
- When `+metric-list` is not explicitly passed `--down-sample`, the granularity is automatically selected based on the time range: `1m` for short ranges, `1h` for medium ranges, and `1d` for long ranges; when explicitly passed, respect the user's specification.
- If the user asks about "page views, PV, UV, or active users," prioritize `+analytics-list`.
- If the user already has `trace_id` or `log_id`, use the corresponding get command directly; if the ID is unknown, list first.
