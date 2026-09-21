# mail send_as


Send mail using a shared mailbox or alias. Applies to sending shortcuts such as `+send` / `+draft-create` / `+reply` / `+reply-all` / `+forward`.

<a id="参数含义"></a>
## Parameter meaning

- `--mailbox` specifies the mailbox the email belongs to (such as `shared@example.com` or `me`); available values can be queried via `accessible_mailboxes`.
- `--from` specifies the sender address in the EML From header (alias, mail group, etc.); available values can be queried via `send_as`.
- When not using a shared mailbox or alias, there is no need to specify `--mailbox`; the behavior is the same as default sending.

<a id="查询可用邮箱和发信地址"></a>
## Query available mailboxes and sending addresses

```bash
# Query accessible mailboxes (primary mailbox + shared mailboxes)
lark-cli mail user_mailboxes accessible_mailboxes --params '{"user_mailbox_id":"me"}'

# Query the available sending addresses of a mailbox (primary address, alias, mail group)
lark-cli mail user_mailbox.settings send_as --params '{"user_mailbox_id":"me"}'
```

<a id="公共邮箱发信"></a>
## Sending from a shared mailbox

```bash
# --mailbox specifies the shared mailbox; the From header automatically uses that mailbox address
lark-cli mail +send --mailbox shared@example.com \
  --to bob@example.com --subject '通知' --body '<p>你好</p>'
```

<a id="别名发信"></a>
## Sending from an alias

```bash
# --mailbox specifies the owning mailbox, --from specifies the alias address
lark-cli mail +send --mailbox me --from alias@example.com \
  --to bob@example.com --subject '测试' --body '<p>你好</p>'
```

<a id="相关命令"></a>
## Related commands

- `lark-cli mail +send` — Send a new email.
- `lark-cli mail +draft-create` — Create a new draft.
- `lark-cli mail +reply` / `+reply-all` — Reply to an email.
- `lark-cli mail +forward` — Forward an email.
