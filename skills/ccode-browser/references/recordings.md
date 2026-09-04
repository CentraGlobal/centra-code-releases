# Browser recording reference

Read this reference when the user asks about a recording, the thread contains an attached recording or event, or an active browser session produces an important moment worth marking.

## Lifecycle and references

Recording is off by default. When the user enables **Browser → Recordings → Record Agent Browser Sessions**, CCode automatically starts a local recording with each MCP or CLI automation session and completes it when the session ends. Agents cannot enable recording through the browser MCP or CLI.

Use recording status when the task depends on capture. It reports the recording ID, state, current offset, attached tab count, enabled frame/console/network policy, and degraded reasons. A normal automation result that was recorded also includes:

- `recording_id`: stable ID used to reopen or query the recording.
- `event_id`: exact event suitable for a retroactive comment anchor.
- `sequence`: monotonically increasing event position.
- `offset_ms`: event time relative to recording start.

Keep these identifiers when reporting an important failure or finding so the user can jump to the same point later.

## Meaningful timeline comments

Add a concise comment when it materially shortens later review—for example, the action that triggered an error, the first visible incorrect state, a surprising console/network result, or the point where a diagnosis was confirmed. Do not comment on every click, snapshot, or successful routine step.

Prefer anchors in this order:

1. Exact `event_id` from the triggering tool response.
2. Exact event `sequence` returned by a recording query.
3. `offset_ms` when the notable point falls between events.
4. The current moment only when the event is happening now and no better anchor exists.

Event and sequence anchors accept `before`, `at`, or `after` placement. A retroactive comment retains both the target timeline offset and the later offset at which the agent created it. Comments can only be added while the original automation session recording remains active.

## Querying timelines

Event queries return newest first and support these kinds:

- `lifecycle`: recording start, completion, interruption, or degradation.
- `tab`: a browser tab attached to or detached from the session.
- `navigation`: committed URL/title/loading state changes with sensitive URL values redacted.
- `automation`: browser commands, results, errors, cursor coordinates, viewport size, and action type when available.
- `console`: bounded, redacted page console output when enabled.
- `network`: the configured metadata, redacted headers, or bounded redacted bodies when enabled.
- `comment`: agent-authored timeline annotations.
- `frame`: a captured viewport changed at this offset; event queries do not include its TIFF bytes.
- `capture_gap`: capture was paused, unavailable, excluded, storage-limited, or otherwise degraded.

Visual capture targets 30+ FPS during browser activity and deduplicates identical frames. A gap between `frame` events can therefore mean the viewport did not change; an actual loss or privacy pause is represented by `capture_gap`. The native player replays frames on a continuous timeline and skips long inactive spans by default. It is a visual replay rather than an MP4 or downloadable video stream.

Use `kinds` / repeated `--kind` flags and a tab ID when only part of the recording matters. `after_sequence` and `before_sequence` are exclusive. To read the whole recording, request up to 100 events, then set `before_sequence` to the lowest sequence returned until `truncated` is false.

## Thread attachments

A whole-recording attachment gives the recording ID, summary, and exact retrieval instructions. Query and paginate that ID rather than assuming the attachment contains every event.

An individual event attachment gives its exact identity and details and may include the nearest captured browser frame. Use that event as the primary context, and query adjacent sequences only when surrounding activity is necessary.

## Privacy and completeness

Recordings remain local and are not synchronized, but they can retain sensitive page pixels and data. CCode applies best-effort redaction to console and network text; this does not make broad disclosure safe. Do not quote secrets or unrelated personal data from a recording, and do not ask the user to broaden capture merely to simplify an agent task.

The user controls frame capture, console capture, network level, body size, excluded origins, retention, and maximum storage. Respect excluded or missing data. If status reports degradation or the timeline contains a capture gap, identify that limitation instead of inferring what happened during the missing interval.
