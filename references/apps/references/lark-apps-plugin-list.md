# apps +plugin-list

> **Local command**: reads the `package.json` in the current directory, and runs in the project root directory (just like npm). **Does not accept `--app-id`**—it is not a remote API command.

Lists the declared plugin packages and their installation status. For runtime command facts, refer to `lark-cli apps +plugin-list --help`.

<a id="何时用"></a>
## When to use

Check which plugins the current project has declared and whether they are installed. A `declared_not_installed` status means you need to run `+plugin-install` to install.

<a id="命令骨架"></a>
## Command skeleton

Run in the project root directory (just like npm, no path needs to be specified).

<a id="示例"></a>
## Examples

```bash
lark-cli apps +plugin-list --format json
```

<a id="输出契约"></a>
## Output contract

- `data.plugins[]` contains `key`, `version`, `status` (`installed` / `declared_not_installed`).
