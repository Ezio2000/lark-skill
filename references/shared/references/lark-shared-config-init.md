# Initial CLI configuration

Run `lark-cli config init` when the CLI has not been configured. For a new application configuration, start this blocking flow in a background/pollable process and read its output:

```sh
lark-cli config init --new
```

The command waits for the user to complete the browser flow or for expiration. Extract returned `verification_url`, `verification_uri_complete`, or `console_url` as applicable.

Treat each URL as opaque: do not decode/re-encode it, change query parameters, or append punctuation inside it. Display the original clickable URL and generate a PNG QR code with `lark-cli auth qrcode <url> --output <path>`. Use ASCII only when requested. Surface the link before waiting so the user can actually complete configuration.
