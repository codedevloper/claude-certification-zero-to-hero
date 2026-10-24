# Setup and First Session

> **Level:** Beginner · **Time:** ~40 min · **Exam relevance:** CCAR-P 7.1, 7.2, 7.3

## In plain English

Getting started takes three steps: install the `claude` command, sign in, and run it inside a project folder. The rest of this page is about working well in that first session: letting Claude explore before it edits, using plan mode for bigger changes, knowing how to stop and undo, and learning the dozen commands you will use every day.

## Why it matters

- **Good habits from day one** (explore, plan, implement, verify) produce better results than jumping straight to edits.
- **A team rollout starts with a repeatable install** and a known authentication path (CCAR-P-7.1).
- **Knowing the diagnostic commands** (`claude doctor`, `/doctor`, `/status`, `/context`) is the first step in supporting other developers (CCAR-P-7.3).

## How it works

### System requirements (as of 2026-10-24)

| Requirement | Supported |
|---|---|
| Operating system | macOS 13.0+; Windows 10 1809+ or Windows Server 2019+; Ubuntu 20.04+; Debian 10+; Alpine Linux 3.19+ |
| Hardware | 4 GB+ RAM; x64 or ARM64 |
| Shell | Bash, Zsh, PowerShell or CMD |
| Network | Internet connection; see the network configuration page for proxies and firewalls |
| Account | Claude Pro, Max, Team or Enterprise; Claude Console; or Amazon Bedrock, Google Cloud, Microsoft Foundry |

### Install

The native installer is the recommended route; it auto-updates in the background.

```bash
# macOS, Linux, WSL
curl -fsSL https://claude.ai/install.sh | bash
```

```powershell
# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```

Alternatives (these do **not** auto-update by default):

```bash
brew install --cask claude-code        # Homebrew, stable channel (claude-code@latest tracks the latest channel)
winget install Anthropic.ClaudeCode    # Windows Package Manager
```

Verify the installation in a **new** terminal:

```bash
claude --version     # prints a version number
claude doctor        # read-only diagnostics: install health, settings validation, warnings
```

> **Note:** Piping a script from the internet into a shell is a trust decision. Organisations often prefer package-manager installs, a pinned version, or a corporate launcher distributed by device management. `minimumVersion` and `requiredMinimumVersion` managed settings let administrators control versions ([page 8](08-team-rollout.md)).

### Sign in

Run `claude` in a project folder. On first use it prompts you to log in through the browser for a Claude subscription or Console account. With a Console account, a "Claude Code" workspace is created automatically for cost tracking. To switch accounts later, use `/login`; `/logout` signs out. Cloud-provider authentication (Bedrock, Google Cloud, Foundry) is configured with environment variables or the `/setup-bedrock` and `/setup-vertex` commands.

### A productive first session

```bash
cd ~/src/acme-checkout
claude
```

1. **Orient.** Ask questions before asking for changes: "what does this project do?", "how are the tests run?", "where is the payment logic?". Claude reads files and runs read-only commands to answer.
2. **Create project memory.** Run `/init`. Claude analyses the codebase and writes a starting `CLAUDE.md` with build commands, test instructions and conventions. Review it and commit it ([page 3](03-claude-md-and-memory.md)).
3. **Plan before large changes.** Press `Shift+Tab` to cycle to **plan mode** (or type `/plan`). Claude explores and proposes a plan without editing source files. Approve or refine the plan, then let it implement.
4. **Give verifiable goals.** "Make `test_applies_loyalty_discount` pass without changing the test" is better than "fix the discount".
5. **Review changes.** `/diff` shows what changed; `/code-review` and `/security-review` analyse the diff.
6. **Undo if needed.** `Esc` interrupts the current action. `Esc` twice (on an empty prompt) or `/rewind` rolls code and conversation back to a checkpoint.
7. **Commit.** Ask Claude to commit with a descriptive message, or do it yourself.

### Everyday commands and shortcuts

| Command or key | What it does |
|---|---|
| `/help` | List commands |
| `/init` | Generate or improve `CLAUDE.md` |
| `/clear` | Start a new conversation with empty context (use between unrelated tasks) |
| `/compact [focus]` | Summarise the conversation to free context, optionally with a focus |
| `/context` | Visualise what is using the context window |
| `/resume`, `claude -c`, `claude -r` | Resume a previous conversation |
| `/rewind` | Roll back code and/or conversation to a checkpoint |
| `/model`, `/effort` | Switch model or effort level |
| `/permissions` | View and edit allow, ask and deny rules |
| `/memory` | Open memory files and toggle auto memory |
| `/mcp` | Manage MCP servers and authentication |
| `/usage` (alias `/cost`) | Token usage and plan usage |
| `/status` | Version, model, account, and which settings sources (including managed) apply |
| `/doctor` | Setup checkup inside a session |
| `/diff` | Review working-tree changes |
| `Shift+Tab` | Cycle permission modes (for example manual, accept edits, plan, auto) |
| `Esc` | Interrupt Claude; Claude keeps work done so far |
| `!` at the start of input | Shell mode: run a command yourself and share its output with Claude |
| `@` | Mention a file path with autocomplete |
| `Ctrl+O` | Toggle the detailed transcript view |

### Permission mode on first launch

With Claude Code v2.1.283 or later, interactive terminal and VS Code sessions start in **auto** mode by default (a background classifier reviews actions such as shell commands and blocks risky ones), unless settings say otherwise. `claude -p` and the Agent SDK start in **default** (manual) mode. Organisations can change the starting mode or disable auto mode with managed settings. [Page 4](04-permissions-and-settings.md) explains each mode.

## Example

A realistic first hour on a fictional repository, written as the prompts a developer would type:

```text
> what does this project do, how is it structured, and how do I run the tests?
> /init
> [Shift+Tab to plan mode]
> We need to add a "gift card" payment method alongside card and PayPal. Look at how the existing
  methods are implemented and propose a plan, including tests. Don't edit anything yet.
> Plan looks good, but put the provider client in src/payments/providers/ like the others. Go ahead.
> run the full test suite and the linter, and fix anything you broke
> /diff
> /security-review
> commit this on a new branch called feature/gift-cards with a descriptive message
```

## Enterprise use case

*Woodgrove Bank* (fictional) prepared a "first day with Claude Code" guide for 400 engineers. Instead of the curl installer, IT distributed Claude Code through its software portal with a pinned version and a managed settings file already in place. The guide asked every engineer to run `claude doctor`, then `/status` to confirm the `Setting sources` line showed the bank's managed policy, before opening any repository. The first exercise was a read-only exploration of a sample service, then `/init` on a sandbox repository, then a plan-mode change reviewed with `/diff`. Support tickets in the first week dropped compared with an earlier tool rollout, because the most common problems (PATH issues, wrong account, missing policy) were caught by `claude doctor` and `/status`.

## Common mistakes

- **`claude: command not found` after installing**: the install directory is not on your PATH yet; open a new terminal or follow the PATH fix in the troubleshooting guide.
- **Signing in with a personal account on a work machine.** Organisations can enforce the login method and organisation with managed settings (`forceLoginMethod`, `forceLoginOrgUUID`).
- **Editing before exploring**, especially on unfamiliar code.
- **Never clearing context**, so one long session accumulates unrelated history.
- **Using Homebrew or WinGet and forgetting to upgrade.** Those installs do not auto-update by default.
- **Approving prompts without reading them.** Prompt fatigue is a real risk; tune allow rules instead.

## Security considerations

- Install from official sources only, and prefer managed distribution in organisations.
- Start in repositories you trust. The workspace trust dialog lists permission rules a repository wants to grant; read it.
- Avoid pasting secrets into prompts; keep `.env` files out of reach with deny rules ([page 4](04-permissions-and-settings.md)).
- `!` shell-mode commands you type run outside the sandbox in most sessions, because the sandbox applies to commands Claude runs.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `claude` not found | PATH not updated | Open a new terminal; see the install troubleshooting page |
| Install command shows no progress | Normal; the installer downloads silently | Wait, then run `claude --version` in a new terminal |
| Logged into the wrong account | Cached credentials | `/logout` then `/login` |
| Settings seem ignored | Invalid JSON or overridden by a higher level | `claude doctor`; `/status` to see sources |
| Search fails | `ripgrep` missing (some Linux distributions) | Install `ripgrep` per the setup page |

## Check your understanding

1. Which command gives read-only installation and settings diagnostics without starting a session?
2. What does `/init` produce, and what should you do with it?
3. How do you get Claude to propose an approach before it edits anything?
4. What is the difference between `/clear` and `/compact`?

<details>
<summary>Answers</summary>

1. `claude doctor` (or `/doctor` inside a session for a setup checkup).
2. A starting `CLAUDE.md` with build and test commands and project conventions; review it, refine it with knowledge Claude could not discover, and commit it for the team.
3. Switch to plan mode with `Shift+Tab` (or `/plan`) and ask for a plan; approve it before implementation.
4. `/clear` starts a new conversation with empty context; `/compact` keeps the same conversation but summarises it to free space, optionally with a focus.

</details>

## Further reading

- [Quickstart](https://code.claude.com/docs/en/quickstart) and [advanced setup](https://code.claude.com/docs/en/setup) (Claude Code Docs)
- [Interactive mode](https://code.claude.com/docs/en/interactive-mode) and [commands reference](https://code.claude.com/docs/en/commands) (Claude Code Docs)
- [Best practices](https://code.claude.com/docs/en/best-practices) (Claude Code Docs)
- [Environment setup for this repository](../00-getting-started/environment-setup.md)
- Previous: [What is Claude Code?](01-what-is-claude-code.md) · Next: [CLAUDE.md and memory](03-claude-md-and-memory.md)
