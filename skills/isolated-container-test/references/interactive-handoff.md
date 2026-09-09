# Interactive handoff

Read this reference only when the user asks to access, inspect, or manually test the running environment.

## Handoff gate

Leave the runtime running only after:

- required containers are healthy;
- schema and focused seed phases have passed or any substitution is disclosed;
- loopback URLs return the expected status;
- CORS, callbacks, and browser origins are correct for the reported URLs;
- the requested login identity maps to local permissions;
- retrying workers cannot create uncontrolled external traffic;
- the worktree status has not been polluted by generated artifacts.

Do not expose services on all interfaces unless the user asks and understands the network impact.

## Report format

Give the user:

1. **State** — running and intentionally retained.
2. **Project** — exact Compose project name and selected configuration files.
3. **URLs** — application, admin, API/docs, and relevant stub endpoints using actual mapped ports.
4. **Login** — existing identity or disposable username, without repeating a password or token.
5. **Selection** — organization, hotel, tenant, or workspace to choose after login.
6. **Fixtures** — scenario names and expected states.
7. **Known gaps** — failed optional seeds, unavailable browser automation, or untested external integrations.
8. **Cleanup** — a copyable command containing the exact project and configuration stack.

## Retention and resume

- Do not create an invisible timer or self-destruct container. The user must control when an interactive environment is removed.
- Record enough identifiers in the response and resource labels for a later agent to resume or clean it safely.
- On resume, verify the project labels, worktree fingerprint, current container mounts, source commit, health, and mapped ports before acting.
- Source hot reload may make the running environment diverge from its original commit; state this when the worktree has changed.

## Cleanup after the user finishes

Use the same Compose project and configuration files that created the runtime. A typical command is:

```bash
docker compose -p <exact-project> -f <base-compose> [-f <override>] \
  down --volumes --remove-orphans
```

Remove uniquely built project images only when confirmed unshared. Remove the temporary harness directory after Compose no longer needs it. Then run `scripts/verify_cleanup.py --project <exact-project>` and report any resource that remains.
