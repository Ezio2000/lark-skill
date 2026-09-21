# apps +plugin-uninstall

> **Local command**: reads the `package.json` in the current directory, and runs in the project root directory (just like npm). **Does not accept `--app-id`**—it is not a remote API command.

Uninstalls a plugin package. For runtime command facts, `lark-cli apps +plugin-uninstall --help` shall prevail.

<a id="何时用"></a>
## When to use

When the user no longer needs a certain plugin capability, uninstall the corresponding plugin package. Before uninstalling, all instances of that plugin should be deleted first.

<a id="命令骨架"></a>
## Command skeleton

- `--name <key>`: the key of the plugin package to uninstall.

Run in the project root directory (just like npm, no path needs to be specified).

<a id="示例"></a>
## Examples

```bash
lark-cli apps +plugin-uninstall --name <plugin-key>
```

<a id="输出契约"></a>
## Output contract

- Delete `node_modules/{key}` + remove the `actionPlugins` entry.
