<a id="发送投递状态"></a>
# Send Delivery Status


Confirm the delivery status after sending, and handle send interception. For command selection, see the "Command Selection" section of [`../index.md`](../index.md).

<a id="查询时机"></a>
## Query Timing

- Immediate send: query immediately after the send succeeds and returns a non-empty `message_id`.
- Scheduled send: do not query immediately; wait until after the scheduled send time, then use the `message_id` produced by the send to query the delivery status.

<a id="立即发送"></a>
## Immediate Send

After the email is sent successfully, if the response contains a non-empty `message_id`, you must call `send_status` to query the delivery status and report it to the user.

```bash
lark-cli mail user_mailbox.messages send_status \
  --params '{"user_mailbox_id":"me","message_id":"<发送返回的 message_id>"}'
```

Returns the delivery status for each recipient (`status`):

| status | Meaning |
|--------|------|
| 1 | Delivering |
| 2 | Delivery failed, retrying |
| 3 | Bounced |
| 4 | Delivered successfully |
| 5 | Pending approval |
| 6 | Approval rejected |

Briefly report the results to the user; if there are abnormal statuses such as bounces or approval rejections, highlight them.

<a id="发送被拦截"></a>
## Send Intercepted

If the send response contains `automation_send_disable_reason` / `automation_send_disable_reference`, it means the email was not actually sent, but was intercepted by mailbox settings.

- Directly show the user the interception reason and the draft open link.
- Do not continue assuming it was sent successfully.
- Do not call `send_status`.

<a id="相关命令"></a>
## Related Commands

- `lark-cli mail +send --confirm-send` — Send a new email.
- `lark-cli mail +reply --confirm-send` / `+reply-all --confirm-send` — Send a reply.
- `lark-cli mail +forward --confirm-send` — Send a forward.
