<a id="循环容器搭建工具专属无-json-tag"></a>
# Recycling Container (exclusive to the builder tool, no JSON tag)

Batch-render lists with the same layout but different data (such as product lists and recommendation lists). **It can only be visually built in the Feishu Card Builder tool; it does not support being implemented by hand-writing card JSON code**—therefore there is no `tag` field that can be directly orchestrated.

<a id="使用方式"></a>
## Usage

1. In the [Card Builder](https://open.feishu.cn/cardkit), add a recycling container component and bind it to an object array variable.
2. Add any display/interactive/column components inside the container, and bind their fields to the child variables of the object array.
3. After publishing the card template, pass in the actual data array via `template_variable` when sending; each element of the array corresponds to one recycling item.

<a id="发送示例模板--变量赋值"></a>
## Sending Example (template + variable assignment)

```json
{
  "type": "template",
  "data": {
    "template_id": "AAqi6xJ8rabcd",
    "template_version_name": "1.0.0",
    "template_variable": {
      "looping": [
        { "title": "**和风陶韵**", "description": "...", "image": { "img_key": "img_v3_xxx" } },
        { "title": "**匠心之作**", "description": "...", "image": { "img_key": "img_v3_yyy" } }
      ]
    }
  }
}
```

Compress and escape the above JSON, then use it as the `content` of `messages.create`, where `msg_type` is `interactive`.

<a id="嵌套--易错点"></a>
## Nesting / Common Pitfalls

- Nested recycling containers are not supported (object array variables do not support nested object array types).
- The number of array elements is the number of rendered items, so the list length can be controlled directly.
- If a recycling container embeds the interactive components of a form container (such as input), the interactive component's `name` (form item identifier) must be bound to a non-duplicate child variable; otherwise, preview/sending will report an error.
