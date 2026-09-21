<a id="提及用户-用户--mentionuser"></a>
# Mention a user (@user / mentionUser)

Applies to: cases where a text node needs to @ a Feishu user (such as "Owner: @Zhang San", "@Li Si please follow up"). A mention is not a standalone node; it is a run within the rich text of a text node and can be mixed with ordinary text.

> Read this page when the user wants to insert an @user mention.

<a id="取值来源强约束"></a>
## Value source (hard constraint)

- This page only covers @user (mentionUser). @document (mentionDoc) is not supported yet.
- `mentionUserId` must be a **real Feishu user open_id** (of the form `ou_xxxxxxxx`).
- When the user only provides a **name**, first use the `lark-contact` skill to resolve the name into an open_id, then fill it into `mentionUserId`.
- **When a real open_id cannot be resolved, stop and confirm with the user; fabricating an id is forbidden**. A fake id will fail to write or will @ the wrong person.

<a id="content-约束关键"></a>
## Content constraint (key)

- For a run with `mentionUserId`, its `content` **must be non-empty**; by convention fill in `"*"` (a single-character placeholder).
  - Reason: conversion references styles by character placeholder; when `content` is an empty string, that mention produces no element at all (silently dropped).
- The literal content of `content` **is not displayed**: what is shown on the whiteboard is the username looked up in reverse by open_id, not the text of `content`. Therefore do not write the username into `content`; just fill in a single `"*"`.
- A run can only be one type: `mentionUserId` and `hyperlink` are **mutually exclusive** and cannot appear in the same run (validation will report an error). When you need "link + @user", split it into two runs.

<a id="骨架示例"></a>
## Skeleton example

Use `WBTextRun[]` for `text`, splitting the @user into an independent run (`content: "*"` + `mentionUserId`), with ordinary text runs before and after:

```json
{
  "type": "text",
  "width": "fit-content",
  "height": "fit-content",
  "text": [
    { "content": "负责人：", "fontSize": 14 },
    { "content": "*", "mentionUserId": "ou_xxxxxxxxxxxxxxxx", "fontSize": 14 },
    { "content": " 请本周内跟进", "fontSize": 14 }
  ]
}
```

Writing to the whiteboard goes through the standard DSL path (`npx -y @larksuite/whiteboard-cli@^0.2.13 -i diagram.json --to openapi --format json | lark-cli whiteboard +update ... --input_format raw`); there is no need to hand-write raw JSON.

<a id="正反例"></a>
## Correct and incorrect examples

Correct:

```json
{ "content": "*", "mentionUserId": "ou_abc123" }
```

Incorrect (content is an empty string → no @user is produced):

```json
{ "content": "", "mentionUserId": "ou_abc123" }
```

Incorrect (writing the username into content → extra placeholder; the display is still determined by uid):

```json
{ "content": "@张三", "mentionUserId": "ou_abc123" }
```

Incorrect (same run as hyperlink → validation reports an error; must be split into two runs):

```json
{ "content": "*", "mentionUserId": "ou_abc123", "hyperlink": "https://xxx.com" }
```

<a id="陷阱"></a>
## Pitfalls

- **content is empty**: the mention is silently dropped, and the @user is not visible on the whiteboard. You must fill in `"*"`.
- **Writing the username into content**: meaningless; the display name is determined by reverse lookup of the open_id; moreover, multiple characters occupy multiple character positions.
- **mentionUserId + hyperlink in the same run**: a run can only be one element type; this will be blocked by validation and must be split into two runs.
- **Using a fake id or the user's Chinese name as the id**: `mentionUserId` only accepts a real open_id; resolve it through `lark-contact` first.
