# apps +plugin-install

> **Local command**: reads the `package.json` in the current directory, and runs in the project root directory (just like npm). **Does not accept `--app-id`**—it is not a remote API command.

Install a plugin package into the project. For runtime command facts, `lark-cli apps +plugin-install --help` is authoritative.

<a id="何时用"></a>
## When to use

When a user wants to integrate AI capabilities or Feishu platform capabilities, the corresponding plugin package must be installed first. Only after installation can a plugin instance be created. For which plugins are available and which one to choose, read the app repository's own skill: `.agents/skills/plugin-guide/SKILL.md`.

**Plugin package ≠ npm package**: plugin packages are written to `actionPlugins`, npm writes to `dependencies`, two independent mechanisms. It is forbidden to use `npm install` in place of this command.

<a id="命令骨架"></a>
## Command skeleton

- `--name <key>`: plugin package key (obtained from the repository Skill's "AI Plugin Directory"). If not passed, batch-installs all plugins declared in `actionPlugins`.
- `--version <ver>`: specify the version (e.g. `1.0.0`). If not passed, installs the latest version.

Run in the project root directory (just like npm, no path needs to be specified).

<a id="示例"></a>
## Examples

```bash
# Install the latest version
lark-cli apps +plugin-install --name <plugin-key>

# Install a specified version
lark-cli apps +plugin-install --name <plugin-key> --version 1.0.0

# Batch-install all declared plugins
lark-cli apps +plugin-install
```

<a id="输出契约"></a>
## Output contract

- If the same version is already installed, it is skipped (status=already_installed).
- On failure, hint indicates the reason (network/version does not exist/package.json missing).
