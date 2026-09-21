<a id="人员-person"></a>
# Person `person`

Displays a single user's avatar/name; click to view their profile card. **Card 2.0**.

<a id="最小示例"></a>
## Minimal example

```json
{
  "tag": "person",
  "user_id": "ou_xxx",
  "show_name": true
}
```

<a id="字段"></a>
## Fields

| Field | Required | Type | Default | Description |
|---|---|---|---|---|
| `tag` | Yes | String | / | Fixed `person` |
| `user_id` | Yes | String | / | Person ID; supports open_id / union_id / user_id |
| `size` | No | String | medium | `extra_small` / `small` / `medium` / `large` |
| `show_avatar` | No | Boolean | true | Whether to show the avatar |
| `show_name` | No | Boolean | false | Whether to show the name |
| `style` | No | String | normal | `normal` / `capsule` (capsule) |
| `margin` | No | String | 0 | Outer margin [-99,99]px |
| `element_id` | No | String | / | Unique identifier; starts with a letter, ≤20 characters |

<a id="易错点"></a>
## Common pitfalls

- The app sending the card must have permission to access user IDs; otherwise, person information cannot be displayed.
