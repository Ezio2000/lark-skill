# markdown +patch


Perform local text replacement on an existing native Markdown file in Drive, and return whether a new version was actually written.

<a id="命令"></a>
## Command

```bash
# Literal replacement
lark-cli markdown +patch \
  --file-token boxcnxxxx \
  --pattern 'hello markdown' \
  --content 'hello patched'

# Regex replacement (RE2)
lark-cli markdown +patch \
  --file-token boxcnxxxx \
  --regex \
  --pattern 'hello (.+)' \
  --content 'hi $1'

# When the regex pattern contains special characters, escape them explicitly
lark-cli markdown +patch \
  --file-token boxcnxxxx \
  --regex \
  --pattern 'version \\(1\\.0\\)' \
  --content 'version (2.0)'

# Delete matched content
lark-cli markdown +patch \
  --file-token boxcnxxxx \
  --pattern ' debug' \
  --content ''

# --pattern / --content also support @file
lark-cli markdown +patch \
  --file-token boxcnxxxx \
  --pattern @./pattern.txt \
  --content @./replacement.md

# Read replacement from stdin
printf 'hi patched\n' | \
  lark-cli markdown +patch \
    --file-token boxcnxxxx \
    --pattern 'hello markdown' \
    --content -

# Preview the underlying orchestration
lark-cli markdown +patch \
  --file-token boxcnxxxx \
  --pattern 'hello markdown' \
  --content 'hello patched' \
  --dry-run
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--file-token` | Yes | Target Markdown file token |
| `--pattern` | Yes | Text to match; treated as a literal by default; supports passing a string directly, `@file`, `-` (stdin) |
| `--content` | Yes | Replacement content; supports passing a string directly, `@file`, `-` (stdin); an empty string `''` is allowed, meaning delete the matched content |
| `--regex` | No | Interpret `--pattern` as a Go RE2 regex; `--content` supports group replacements such as `$1`; if you need a literal `$`, write it as `$$` |

<a id="关键约束"></a>
## Key constraints

- Currently only **a single group** of `--pattern` / `--content` is supported
- `--pattern` must be passed explicitly and cannot be an empty string
- `--content` must be passed explicitly, but an empty string is allowed
- Without `--regex`, the behavior is equivalent to performing `strings.ReplaceAll` on the entire Markdown text
- With `--regex`, the behavior is equivalent to performing a full RE2 replacement on the entire Markdown text; `$1` and `${name}` in `--content` are interpreted according to the Go regexp replacement template; for a literal `$`, write it as `$$`
- The final Markdown after replacement cannot be empty; if the patch result is an empty string, the CLI will error out directly and will not upload an empty file, because Drive does not support zero-byte Markdown, and an empty file is usually a mistake
- When `0` matches, the command still returns successfully, but no new version is uploaded

## Good / Bad

```bash
# BAD: the pattern contains regex special characters but they are not escaped, making it easy to match the wrong position
lark-cli markdown +patch \
  --file-token boxcnxxxx \
  --regex \
  --pattern 'version (1.0)' \
  --content 'version (2.0)'

# GOOD: explicitly escape the parentheses and the dot
lark-cli markdown +patch \
  --file-token boxcnxxxx \
  --regex \
  --pattern 'version \\(1\\.0\\)' \
  --content 'version (2.0)'
```

<a id="实现边界"></a>
## Implementation boundaries

- The internal semantics of this command are: **download -> local replace -> overwrite upload**
- It is not a server-side atomic patch; if someone updates the same file after you download it and before you upload, this patch may still overwrite that intermediate modification
- It does not return detailed match positions, only the number of hits
- `--dry-run` will show both possible upload paths at the same time: `upload_all` (small files) and `upload_prepare/upload_part/upload_finish` (large file multipart upload)

<a id="返回值"></a>
## Return value

Matched and wrote a new version:

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "updated": true,
    "mode": "literal",
    "match_count": 1,
    "version": "7639217385152646325",
    "size_bytes_before": 39,
    "size_bytes_after": 41
  }
}
```

No match:

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "updated": false,
    "mode": "literal",
    "match_count": 0,
    "version": "",
    "size_bytes_before": 41,
    "size_bytes_after": 41
  }
}
```

Where:

- `updated` indicates whether a new version was actually uploaded this time
- `mode` is `literal` or `regex`
- `match_count` is the number of matches
- `version` only has a value when `updated=true`
- `size_bytes_before` / `size_bytes_after` are the Markdown sizes before and after replacement, respectively

<a id="适用场景"></a>
## Applicable scenarios

- You only need to replace a small section of Markdown text without manually `fetch -> edit -> overwrite` yourself
- You need to do simple batch replacement based on regex
- You need to determine "whether the content was actually changed this time"

<a id="不适用场景"></a>
## Not applicable scenarios

- You need rename / move / delete / permission / comment management: switch to [`lark-drive`](../../drive/index.md)
- You need multiple groups of patches done in one go: currently not supported; instead call `markdown +patch` multiple times
- You need a truly atomic update: the current capability does not provide this

<a id="参考"></a>
## References

- [lark-markdown](../index.md) — Markdown domain overview
- [lark-shared](../../shared/index.md) — authentication and global parameters
