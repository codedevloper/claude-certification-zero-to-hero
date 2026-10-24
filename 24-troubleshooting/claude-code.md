# Troubleshooting: Claude Code

> **As of 2026-10-24**, checked against the official [Claude Code docs](https://code.claude.com/docs/en/overview),
> including [settings](https://code.claude.com/docs/en/settings), [permissions](https://code.claude.com/docs/en/permissions),
> [memory](https://code.claude.com/docs/en/memory), [hooks](https://code.claude.com/docs/en/hooks) and
> [troubleshooting](https://code.claude.com/docs/en/troubleshooting). Concepts: [09 · Claude Code](../09-claude-code/README.md).

## Your first three commands

| Command | Tells you |
|---|---|
| `claude doctor` (terminal) or `/doctor` (in session) | Install health, settings-file validation errors, configuration problems |
| `/status` | Version, model, account and the **Setting sources** actually loaded |
| `/context` | What is using the context window, including which memory files loaded |

## Installation and sign-in

**Symptom:** `claude: command not found`, an old version, or sign-in loops.

**Likely causes:** the install location is not on `PATH`; several installs compete; a corporate proxy blocks sign-in;
`ANTHROPIC_API_KEY` set in the shell overrides your subscription login.

**Diagnosis:** `which -a claude`, `claude --version`, `claude auth status`.

**Fix:** follow the official setup page for your OS; remove duplicate installs; `claude update`; configure proxy
variables per the docs; unset an unintended `ANTHROPIC_API_KEY` or sign in with `claude auth login --console` if you
intend API billing.

## CLAUDE.md is ignored

**Symptom:** Claude does not follow project conventions you wrote down.

**Likely causes:**

- The file is in the wrong place or not loaded (started Claude Code in a different directory).
- A subdirectory `CLAUDE.md` loads only once Claude touches files in that subdirectory.
- An `@import` points outside the project and was not approved.
- The file is long and vague, so instructions compete.
- You expected enforcement; `CLAUDE.md` is context, not a control.

**Diagnosis:** run `/context` and check the **Memory files** list; run `/memory` to see which files are in play.

**Fix:** put team rules in `./CLAUDE.md` or `./.claude/CLAUDE.md`; keep it short and specific (the docs suggest under
200 lines); move file-type rules to `.claude/rules/` with `paths`; approve external imports; for anything that must
always or never happen, use a **permission rule or a hook** instead.

## Settings do not apply

**Symptom:** a key you set seems ignored.

**Likely causes:** a higher level sets the same key (managed → command line → project local → shared project → user);
invalid JSON (comments or trailing commas are not allowed); the key is not allowed in that file (for example
`permissions.defaultMode` values `auto` and `bypassPermissions` do not take effect from project files); a key read
only at startup; the project folder is not trusted yet.

**Diagnosis:** `/status` (Setting sources), `claude doctor` (rejected entries), check the key's scope in the
[settings reference](https://code.claude.com/docs/en/settings-reference).

**Fix:** move the key to the right file; fix the JSON; restart for start-up keys; trust the folder; ask an admin if a
managed setting overrides you.

## Too many permission prompts, or not enough

**Symptom:** Claude asks for approval on every test run, or does things you expected to be blocked.

**Likely causes:** no allow rules for routine commands; rules too narrow (`Bash(npm test)` does not match
`npm test -- --watch`); evaluation order misunderstood (**deny → ask → allow**, first match wins); an `ask` rule in a
shared file outranks your local allow; a permissive mode such as `acceptEdits` or `bypassPermissions`.

**Diagnosis:** `/permissions` lists rules by scope; read the prompt text to see the exact tool and argument.

**Fix:**

```json
{
  "permissions": {
    "allow": ["Bash(npm run test *)", "Bash(npm run lint)", "Bash(git status)", "Bash(git diff *)"],
    "deny":  ["Read(./.env)", "Read(./secrets/**)", "Bash(git push --force *)"]
  }
}
```

Use wildcards deliberately; put team rules in `.claude/settings.json`; reserve `bypassPermissions` for disposable
sandboxes.

## A hook does not run, or blocks everything

**Symptom:** the hook never fires, or every tool call is blocked.

**Likely causes:**

| Cause | Detail |
|---|---|
| Wrong event or matcher | Matchers match `tool_name` for tool events; `Edit\|Write` is a list; other characters make it a regex |
| Matcher on an event without matcher support | `UserPromptSubmit`, `Stop` and others ignore `matcher` |
| Script not executable or wrong path | Use `${CLAUDE_PROJECT_DIR}` for project-relative paths; `chmod +x` |
| Script reads arguments instead of stdin | Hooks receive event JSON on **stdin** |
| Exit code misunderstood | `0` success; `2` blocks (stderr is the reason) on events that can block; other codes are non-blocking errors |
| Exit 2 on an event that cannot block | `PostToolUse`, `Notification`, `SessionEnd` cannot block |
| Timeout | Default 600 s for command hooks; set `timeout` |

**Diagnosis:** `/hooks` shows the loaded configuration; run the script by hand with sample JSON on stdin; run Claude
Code with `--verbose`.

**Fix:** correct the event and matcher; read stdin with a JSON parser; return `2` only when you intend to block; keep
hooks fast and deterministic.

## Context fills up, Claude forgets earlier work

**Symptom:** quality drops in long sessions; auto-compaction happens often.

**Fix:** `/clear` between unrelated tasks; `/compact` with focus instructions; use subagents for searches and log
reading (their output stays out of your main context); keep `CLAUDE.md` lean; turn off MCP servers you are not using
(their tool definitions consume context).

## Changes went wrong

**Symptom:** Claude edited the wrong files or took a bad approach.

**Fix:** `/rewind` to restore a checkpoint (conversation and/or code); work on a branch; use `plan` mode first for
risky changes; review diffs before committing.

## Headless (`-p`) runs fail in CI

**Symptom:** works locally, fails or hangs in CI.

**Likely causes:** the job waits for a permission prompt; missing credentials; no turn limit; settings files not
present in the runner.

**Fix:** pre-approve exactly the tools needed with `--allowedTools`; choose a non-interactive permission mode; add
`--max-turns`; use `--output-format json` and check the exit code; inject credentials from the CI secrets store;
commit `.claude/settings.json`. After a `-p` run that ignored a setting, run `claude doctor` to see what was dropped.

## MCP servers in Claude Code

See the dedicated [MCP troubleshooting page](mcp.md). Quick checks: `claude mcp list`, `/mcp` for status and OAuth,
`MCP_TIMEOUT` for slow-starting servers, `MAX_MCP_OUTPUT_TOKENS` for large outputs.
