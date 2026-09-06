# Hermes Temporal Memory

`temporal-memory` is a Hermes general plugin that keeps procedural skills separate from learned world constraints. It observes tool calls and explicit events, then uses one explicit LLM extraction to write a candidate temporal document.

## Ubuntu installation

On the Ubuntu machine where Hermes is installed, copy only this source directory (not Python's generated `__pycache__` folders):

```bash
mkdir -p ~/.hermes/plugins
cp -a /path/to/hermes-temporal-memory ~/.hermes/plugins/temporal-memory
hermes plugins enable temporal-memory
hermes plugins list
```

The last command should show `temporal-memory` enabled. Data is stored outside the plugin install directory in Hermes' plugin-data folder. Set `HERMES_TEMPORAL_MEMORY_DIR` to override it, which is useful for an AIWiki repository.

## Workflow

1. Run a normal task. The plugin records user intent and non-temporal tool calls.
2. When the task is complete, invoke `/temporal-learn capture-dut-trigger` in the same interactive session to create a candidate `temporal/<task>.yaml`. The optional text is the task name, not the trace identifier. In a headless or multi-session setup, pass an explicit trace identifier as `/temporal-learn session:<session-id>`.
3. Use `temporal_query` and `temporal_check` in later tasks. Promote candidate rules to canonical AIWiki knowledge only after independent validation.

`auto_extract` is disabled by default to avoid an LLM call at the end of every Hermes `run_conversation` call. Enable it in the plugin settings only if that cost and cadence fit your workflow.

## Agent tools

- `temporal_record_event` records device state or an event that a tool result did not expose.
- `temporal_query` returns matching learned candidate rules.
- `temporal_check` checks a proposed action against learned prerequisites supplied as `current_states`.

## Important integration note

This MVP deliberately does not override Hermes' built-in `/learn`. It runs beside it: `/learn` produces `SKILL.md` (how), while `/temporal-learn` produces a candidate temporal document (when/why). That avoids coupling to internal `/learn` output formats and keeps model spending explicit.

## End-to-end smoke test

1. Start `hermes chat` and complete a small workflow with at least two tool calls, for example creating and then reading a scratch file.
2. Optionally record an explicit state: ask the agent to call `temporal_record_event` with `task: smoke-test`, `event: scope_armed`, `source: test`, and `state: scope.armed`.
3. In that same chat, run `/temporal-learn smoke-test`. Hermes performs one structured LLM call and returns the saved candidate document path.
4. Ask the agent to call `temporal_query` with `query: smoke test`. It should return the candidate document and its extracted constraints.
5. Check the document under `~/.hermes/plugin-data/temporal-memory/temporal/` (or your `HERMES_TEMPORAL_MEMORY_DIR` override). It must have `status: candidate`; review and validate it before any later AIWiki promotion.
