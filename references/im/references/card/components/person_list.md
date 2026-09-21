<a id="人员列表-person_list"></a>
# Person list `person_list`

Displays the avatars/names of multiple users. **Card 2.0**.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "person_list",
  "persons": [{ "id": "ou_xxx" }, { "id": "ou_yyy" }]
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `person_list` |
| `persons` | Yes | Array | / | Each item is `{ id }`; id supports open_id / union_id / user_id |
| `show_name` | No | Boolean | true | Whether to show names; when turned off and there are multiple people, uses the "gourd string" stacked avatar style |
| `show_avatar` | No | Boolean | false | Whether to show avatars |
| `size` | No | String | medium | `extra_small` / `small` / `medium` / `large` |
| `lines` | No | Int | / | Maximum number of lines, cannot be 0 |
| `drop_invalid_user_id` | No | Boolean | false | true ignores invalid IDs; false reports an error when there are invalid IDs |
| `icon` / `ud_icon` | No | Object | / | Prefix icon (same as `div.icon`); if both are set, `icon` takes precedence |
| `margin` | No | String | 0 | Outer margin [-99,99]px |
| `element_id` | No | String | / | Unique identifier, starts with a letter, ≤20 characters |

<a id="易错点"></a>
## Common pitfalls

- The app sending the card must have permission to access user IDs, otherwise person information cannot be displayed.
