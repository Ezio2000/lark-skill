# Extend this skill

Capture reusable Lark operations in this bundle. Keep a single discovery entrypoint unless the user explicitly requests a separate skill.

## Where to put guidance

- Extend the existing module's `index.md` or operation references for an existing domain.
- Add `references/<domain>/index.md` and an entrypoint routing row for a substantial new domain or workflow.
- Add a module-local script only for repeated deterministic logic. Manage Python through uv.
- Link shared authentication and confirmation rules instead of copying them into each operation. Do not create forwarding-only skills.

## Establish the API contract

Inspect `lark-cli <service> --help` and `lark-cli schema <service.resource.method>`. Prefer shortcuts, then registered APIs. Use [OpenAPI discovery](../openapi-explorer/index.md) when neither covers the operation. Verify the method, path, fields, scopes, identities, and returned identifiers.

Describe triggers, inputs, command selection, data flow, platform limits, pagination, identity continuity, and recoverable failures. Complete parameters allow direct execution; avoid routine login, broad preloading, or repeated confirmation.

Put substantial field tables and examples in operation references. A reusable workflow does not itself authorize sending, publishing, deleting, or broadening the user's task.

## Validate

Check entrypoint routing, local links, resource paths, and new scripts. Use representative behavior scenarios as well as structural tests. Validate remote writes only against user-authorized targets. Keep temporary reports and fixtures out of the delivered bundle.
