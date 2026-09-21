# minutes +speaker-replace


Replace the speaker identity in a Minutes verbatim transcript: reassign all speech segments corresponding to the "original speaker" in the Minutes verbatim transcript to the "new speaker". This is commonly used to resolve incorrect automatic speaker recognition in Minutes, or to rebind an external/non-Feishu speaker to the correct Feishu user.

This module corresponds to shortcut: `lark-cli minutes +speaker-replace`.

<a id="典型触发表达"></a>
## Typical trigger expressions

- "Change A's speech in this Minutes to B"
- "The Minutes speaker was recognized incorrectly, help me replace Zhang San's parts with Li Si"
- "Change the speech of an external speaker / non-Feishu speaker in the Minutes to a certain Feishu user"
- "Minutes speaker modification / replacement / reassignment"

<a id="完整工作流"></a>
## Complete workflow

After identifying a "modify Minutes speaker" request, you **must** execute in the following order; it is **forbidden** to pass the display name directly to `--from-speaker-id`.

1. **Confirm `minute_token`**
   - Obtain `minute_token` from the Minutes URL, search, or VC link.

2. **Query the speaker list (must be done first)**
   - Use **`lark-cli api`** to directly call the internal HTTP interface:
     ```bash
     lark-cli api GET "/open-apis/minutes/v1/minutes/<minute_token>/transcript/speakerlist" --as user
     ```
   - Returns `data.speakers[]`, each item contains `speaker_id` (opaque id) and `name` (verbatim transcript display name). Example:
     ```json
     {
       "data": {
         "speakers": [
           {"speaker_id": "ENCRYPTED_TOKEN_ABC", "name": "说话人1"},
           {"speaker_id": "ENCRYPTED_TOKEN_DEF", "name": "说话人2"}
         ]
       }
     }
     ```

3. **Parse `--from-speaker-id`**
   - Based on the original speaker described by the user (display name, such as "Speaker 1" or "Zhang San"), perform an **exact match** by `name` in `speakers[]`, and take the corresponding **`speaker_id`** as the value of `--from-speaker-id`.
   - **`--from-speaker-id` only passes `speaker_id`, not the display name.**
   - If there are multiple entries with the same name (same `name`, different `speaker_id`): **do not choose arbitrarily**. You may use [`minutes +detail --transcript`](lark-minutes-detail.md) to compare each person's speech content, and after the user confirms, use the exact `speaker_id`.
   - If there is no matching display name in the list: inform the user and verify the spelling, or ask the user to confirm the label on the Minutes page.

4. **Parse `--to-user-id`**
   - The new speaker must be an open_id starting with `ou_`. If the user only provides a name, first use [lark-contact](../../contact/index.md) to resolve it.

5. **Execute the replacement**
   ```bash
   lark-cli minutes +speaker-replace \
     --minute-token obcnxxxxxxxxxxxxxxxxxxxx \
     --from-speaker-id ENCRYPTED_TOKEN_ABC \
     --to-user-id ou_new_speaker_open_id
   ```

<a id="命令示例"></a>
## Command examples

```bash
# 1. First query the list (raw HTTP call)
lark-cli api GET "/open-apis/minutes/v1/minutes/obcnxxxxxxxxxxxxxxxxxxxx/transcript/speakerlist" --as user

# 2. Then replace (from-speaker-id comes from the speaker_id in the previous step)
lark-cli minutes +speaker-replace \
  --minute-token obcnxxxxxxxxxxxxxxxxxxxx \
  --from-speaker-id ENCRYPTED_TOKEN_ABC \
  --to-user-id ou_new_speaker_open_id
```

<a id="参数"></a>
## Parameters

| Parameter | Required | Description |
|------|------|------|
| `--minute-token <token>` | Yes | The unique identifier of the Minutes, which can be extracted from the end path of the Minutes URL |
| `--from-speaker-id <id>` | Yes | The original speaker being replaced **`speaker_id`** (from the `data.speakers[].speaker_id` of the speakerlist API) |
| `--to-user-id <ou_xxx>` | Yes | The new speaker, **must be an open_id starting with `ou_`**, usernames are not supported |

<a id="核心约束"></a>
## Core constraints

<a id="1-必须先查-speakerlist再替换"></a>
### 1. Must query speakerlist first, then replace

The Agent must first `lark-cli api GET .../speakerlist`, then `+speaker-replace`; `--from-speaker-id` only accepts `speaker_id`.

`+speaker-replace` will **not** request speakerlist on its own: the value of `--from-speaker-id` will be sent as-is to the replacement interface. The entire chain only queries speakerlist once at the beginning by the Agent, so be sure to pass in the `speaker_id` obtained in the previous step (do not pass the display name, otherwise the replacement interface will return speaker-not-found).

<a id="2-新说话人必须是-open_id"></a>
### 2. The new speaker must be an open_id

`--to-user-id` only supports open_id starting with `ou_`, and **does not support passing a name directly**; if the user only provides a name, first use [lark-contact](../../contact/index.md) to resolve the name into `open_id`.

<a id="3-历史参数"></a>
### 3. Historical parameter

There is a hidden historical parameter `--from-user-id` (the open_id of the Feishu speaker), retained only for backward compatibility; new workflows should always use `--from-speaker-id` + `speaker_id`.

<a id="认证与权限"></a>
## Authentication and permissions

- Required scopes: `minutes:minutes:readonly` (internal speaker resolution), `minutes:minutes:update` (execute replacement).

<a id="输出结果"></a>
## Output result

| Field | Description |
|------|------|
| `minute_token` | The modified Minutes Token, consistent with the input `--minute-token` |
| `from_speaker_id` | The opaque speaker identifier actually used for replacement |
| `to_user_id` | The new speaker open_id after replacement, consistent with the input `--to-user-id` |

<a id="相关场景"></a>
## Related scenarios
- [Generate and modify Minutes](../scenes/create-and-edit-minutes.md)
