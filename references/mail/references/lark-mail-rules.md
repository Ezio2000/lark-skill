<a id="收信规则-shortcut"></a>
# Incoming Mail Rules Shortcut

Manage rules for automatically processing received mail. Prefer the `mail +rule-*` shortcut, writing conditions and actions via stable English aliases; fall back to the `mail user_mailbox.rules` atomic raw command only when server-side fields not yet modeled by the current shortcut are needed. Rule write operations must use real `rule_id`; do not guess IDs. Creating, updating, and deleting rules require user confirmation per the high-risk write rules in index.md and passing `--yes`; enabling/disabling and reordering are ordinary write operations and are exempt from `--yes`.

<a id="常用-shortcut"></a>
## Common shortcuts

```bash
# List rules, outputting semantic_spec, description, unknowns
lark-cli mail +rule-list --as user --user-mailbox-id me --format json

# View a single rule
lark-cli mail +rule-get --as user --user-mailbox-id me --rule-id "<rule_id>"

# dry-run create: mark as read when the subject contains Alpha, producing no server-side side effects
lark-cli mail +rule-create --as user --dry-run \
  --name "Alpha通知已读" \
  --condition "subject:contains:Alpha" \
  --action "mark_read"

# Create the same rule
lark-cli mail +rule-create --as user \
  --name "Alpha通知已读" \
  --condition "subject:contains:Alpha" \
  --action "mark_read" \
  --yes

# Update rule: fields not passed are first read from the current rule and preserved; passing --condition/--action replaces the corresponding complete set
lark-cli mail +rule-update --as user \
  --rule-id "<rule_id>" \
  --name "Alpha通知归档" \
  --action "archive" \
  --yes

# Enable/disable rule
lark-cli mail +rule-disable --as user --rule-id "<rule_id>"
lark-cli mail +rule-enable --as user --rule-id "<rule_id>"

# Delete rule: a real deletion must explicitly pass --yes; when unsure, use --dry-run first
lark-cli mail +rule-delete --as user --rule-id "<rule_id>" --dry-run
lark-cli mail +rule-delete --as user --rule-id "<rule_id>" --yes

# Adjust order: choose either a complete order or a single move
lark-cli mail +rule-reorder --as user --rule-ids "<rule_id_1>,<rule_id_2>,<rule_id_3>"
lark-cli mail +rule-reorder --as user --move-rule-id "<rule_id_3>" --before-rule-id "<rule_id_1>"
```

<a id="alias-速查"></a>
## Alias quick reference

Condition grammar:

```text
--condition field:op:value
--condition field:op
--condition field
```

Common fields: `from`/`sender`, `to`/`recipient`, `cc`, `to_or_cc`, `subject`/`title`, `body`, `attachment_name`, `attachment_type`, `any_address`, `all_mail`/`all`, `external`, `spam`, `not_spam`, `has_attachment`.

Common operators: `contains`/`include`, `not_contains`/`exclude`, `starts_with`/`prefix`, `ends_with`/`suffix`, `equals`/`eq`/`is`, `not_equals`/`ne`, `contains_self`/`self`, `empty`/`is_empty`.

Action grammar:

```text
--action kind
--action kind:key=value
--action kind:json={"key":"value"}
```

Common actions: `archive`, `delete_mail`/`trash`, `mark_read`/`read`, `move_spam`/`spam`, `not_spam`/`never_spam`, `star`/`flag`, `mute_notification`/`mute`, `move_folder:folder_id=<id>`.

`--conditions` / `--actions` support JSON or `@file`. JSON example:

```json
[
  {"field":"subject","operator":"contains","value":"Alpha"},
  {"field":"has_attachment"}
]
```

<a id="unknown-raw-策略"></a>
## Unknown raw strategy

- Read path is lenient: `+rule-list` / `+rule-get` still output rules when encountering unknown enums or extension fields, `unknowns[]` explains unrecognizable raw fragments, and `raw` preserves the original rule.
- Update rule: `+rule-update` is "change whatever is passed". When only changing the name, enable/disable, match, or stop-after-match, untouched raw is preserved; passing a new `--condition(s)` replaces condition items, and if `--match` is not passed the current match_type is preserved; passing a new `--action(s)` replaces action items.
- Input validation: when the user inputs an alias/semantic string, it must map to an enum supported by the current shortcut, otherwise an error is raised; if the user directly inputs an enum number unknown to the current shortcut, an error is also raised.
- raw fallback: when server-side fields not yet modeled by the current shortcut need to be written, read `raw` and then use the atomic `user_mailbox.rules` command.

<a id="原子-raw-fallback主题包含文本--标记为已读"></a>
## Atomic raw fallback: subject contains text → mark as read

```bash
# 1. Create rule: mark as read when the subject contains the specified text
lark-cli mail user_mailbox.rules create --as user \
  --params '{"user_mailbox_id":"me"}' \
  --data '{"name":"<rule_name>","is_enable":true,"ignore_the_rest_of_rules":false,"condition":{"match_type":1,"items":[{"type":6,"operator":1,"input":"<subject_text>"}]},"action":{"items":[{"type":3}]}}'

# 2. Verify rule
lark-cli mail user_mailbox.rules list --as user \
  --params '{"user_mailbox_id":"me"}'

# 3. Delete rule
lark-cli mail user_mailbox.rules delete --as user \
  --params '{"user_mailbox_id":"me","rule_id":"<rule_id>"}' \
  --yes
```

Quick codes above: condition `type=6` = subject, `operator=1` = contains, action `type=3` = mark as read.

<a id="原生-api"></a>
## Native API

Incoming mail rules use the `user_mailbox.rules` resource. When parameters are uncertain, run first:

```bash
lark-cli mail user_mailbox.rules -h
lark-cli schema mail.user_mailbox.rules.<method>
```
