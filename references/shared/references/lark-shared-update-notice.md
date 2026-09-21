# Updates and notices

This is a locally maintained single skill named `lark`, with domain resources in `references/<domain>/`. The CLI-managed `lark-suite` layout is separate, not an alias for this bundle.

`_notice.update`, `_notice.skills`, and deprecation hints do not interrupt business work or authorize automatic upgrades, installations, or restoration of removed split skills. Handle them when the user asks or an upgrade is needed for the task.

Inspect documentation embedded in the installed CLI when comparing command behavior:

```sh
lark-cli skills read lark-doc references/lark-doc-fetch.md
lark-cli skills list
lark-cli update --help
```

Embedded documentation ships with the binary but excludes scripts/assets. Use it to compare contracts, then update only affected local references while preserving the unified entrypoint and user rules.

For an authorized upgrade, inspect the installation method and current update help. The baseline updater can install AI skills and offers `--skills-layout separate|suite`; avoid leaving split skills or a second `lark-suite` alongside this skill. If the CLI-managed update is needed, preserve this bundle in a temporary backup, inspect the actual generated directories, merge necessary changes, and remove only duplicates created by that update. Preserve unrelated skills and personal modifications.

A deprecated command's suggested replacement may be used on the next equivalent call after checking parameter compatibility. Do not redo an already successful operation just to use the replacement.

Suppress notices for one command when stable machine output is needed:

```sh
LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1 <lark-cli command>
```
