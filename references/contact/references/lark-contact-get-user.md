# +get-user

Get basic user information (name, etc.) by ID.

```bash
# Get yourself
lark-cli contact +get-user --as user

# bot gets another user by ID
lark-cli contact +get-user --user-id ou_xxx --as bot

# Get by union_id / user_id (defaults to open_id)
lark-cli contact +get-user --user-id <id> --user-id-type union_id --as bot
```

<a id="注意事项"></a>
## Notes

- **To get another user by ID with user identity, use `+search-user --user-ids <id>`**, which has more fields than this command (department / email / whether activated, etc.). The user mode of this command returns only a few fields.
- **`--as bot` must pass `--user-id`**: omitting it will directly cause an error (only user identity can omit `--user-id` to get yourself).
