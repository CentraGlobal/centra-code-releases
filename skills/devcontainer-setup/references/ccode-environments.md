# CCode `environments.json`

Read this reference whenever creating or editing the environment declarations that accompany a CCode dev-container configuration.

## Location and Container Keys

Place the file beside its configuration:

- `.devcontainer/devcontainer.json` → `.devcontainer/environments.json`
- `.devcontainer/backend/devcontainer.json` → `.devcontainer/backend/environments.json`

Each entry under `containers` is isolated from the others:

- For Docker Compose, use the exact service name from the rendered Compose configuration.
- For an image- or Dockerfile-based dev container, use the exact `name` from `devcontainer.json`.

An empty but valid starting document is:

```json
{
  "version": 1,
  "containers": {
    "project-name": {
      "variables": {}
    }
  }
}
```

`environments.json` is strict JSON. Do not add comments or trailing commas.

## Variable Declarations

Every variable declares exactly one source:

- `value`: plaintext committed to the repository. Use only for a safe development default.
- `secret`: a logical identifier whose value CCode stores in the local credential store. The secret value does not belong in this file.

Example:

```json
{
  "version": 1,
  "containers": {
    "api": {
      "variables": {
        "APP_ENV": {
          "value": "development",
          "consumers": ["dev_container_runtime"]
        },
        "DATABASE_URL": {
          "secret": "database-url",
          "required": true,
          "consumers": ["dev_container_runtime"]
        },
        "PACKAGE_REGISTRY_TOKEN": {
          "secret": "package-registry-token",
          "required": true,
          "consumers": ["dev_container_build"]
        }
      }
    }
  }
}
```

Rules enforced by CCode:

- `version` must be `1`.
- Unknown fields are rejected.
- Variable names use uppercase ASCII environment-variable form: the first character is `A-Z` or `_`; remaining characters are `A-Z`, `0-9`, or `_`.
- Logical secret identifiers use lowercase ASCII letters or digits separated by single hyphens. They must start with a letter and cannot end with a hyphen.
- `required` defaults to `false`. It is most useful for secrets: container creation fails clearly when a required secret has not been configured.
- `consumers` is required and is an array. For container creation, use `dev_container_build` and/or `dev_container_runtime` as appropriate.
- `exported_secret_values` is archive-only and must never be stored in the workspace's `environments.json`.

Build values are shared while CCode resolves a configuration. Declaring different build values for the same variable in different containers is an error. Runtime values remain scoped to their container entry.

Treat `dev_container_build` as configuration-time input, not as proof that the value is protected from image layers or build logs. Do not pass a long-lived secret into a Dockerfile `ARG` or `RUN` step that can persist or print it. Prefer runtime secrets; when a true build secret is unavoidable, require an explicitly reviewed BuildKit secret design rather than improvising one.

## Supplying and Applying Values

Developers set logical secrets in CCode through the Containers panel:

1. Open the service context menu.
2. Choose **Environment Variables…**.
3. Enter the value for the existing secret-backed declaration.
4. Save the changes.

Environment changes do not alter an existing container. Recreate the affected container after changing runtime values. Changes to `devcontainer.json` likewise require stopping the existing container and reopening the project in the dev container.

When handing off, list the environment variable name and logical secret identifier, but never include or request the secret value in chat or committed files.
