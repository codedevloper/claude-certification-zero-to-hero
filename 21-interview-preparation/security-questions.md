# AI Security Interview Questions

Twenty-eight questions for AI security engineer, application security, DevSecOps and security architect roles, with
model answers. They cover threat modelling, prompt injection, agents and tools, MCP, data protection, supply chain,
governance and incident response. All questions are original.

> **How to use this page:** strong security answers name the threat, explain why it works, then give **layered**
> controls that do not depend on the model behaving. Mapped to the
> [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) where relevant. See also the
> [AI security cheat sheet](../22-cheat-sheets/ai-security.md) and [12 · AI security](../12-ai-security/README.md).

---

## Threat modelling and principles

### 1. How is threat modelling an LLM application different from a normal web app?

**Model answer:** The usual assets and boundaries still apply, but there are new ones. Natural-language input can
change program behaviour (instructions and data share a channel), so every piece of text the model reads is a
potential control input. The model's output is untrusted data that may flow into tools, HTML, SQL or other systems.
Agents add delegated authority: the model can take actions with real credentials. And behaviour is probabilistic, so
you cannot rely on a test showing an attack "does not work". I map data flows including retrieved content, tool calls
and memory; apply STRIDE with LLM-specific questions; and design controls that assume the model can be manipulated.

### 2. What does "treat the model as an untrusted component" mean in practice?

**Model answer:** Assume an attacker can make the model say or request anything. Then: authorisation is enforced in
code for the end user, not by the prompt; tool inputs are validated against schemas and business rules; outputs are
encoded before rendering and parameterised before queries; consequential actions need human approval or deterministic
policy; secrets never enter the context; and logs let you reconstruct what happened. The model is a powerful, fallible
decision helper inside a box with locked doors.

### 3. Which OWASP LLM risks worry you most for an agent with tools, and why?

**Model answer:** Prompt injection (LLM01) because it is the entry point, excessive agency (LLM06) because it turns a
manipulated model into real-world impact, and sensitive information disclosure (LLM02) because agents often hold broad
data access. Improper output handling (LLM05) is close behind when outputs feed other systems. Unbounded consumption
(LLM10) matters for cost and availability in loops. The combination of injected instructions, private data access and
an outbound channel is the classic exfiltration chain, so I design to break at least one link.

## Prompt injection

### 4. Explain direct and indirect prompt injection with an example of each

**Model answer:** Direct injection is the user typing instructions to override the system, such as asking the
assistant to ignore its rules and reveal internal configuration. Indirect injection hides instructions in content the
model processes on someone else's behalf: a web page, an email, a PDF, a ticket, a tool result. For example, a vendor
invoice processed by an accounts-payable agent contains white-on-white text telling the agent to change the bank
details on file. Indirect injection is more dangerous because the victim is not the attacker and the payload arrives
through trusted-looking channels.

### 5. Can prompt injection be fully prevented by a better system prompt?

**Model answer:** No. Instructions and data travel in the same medium, and model robustness, while improving, is
probabilistic. A good system prompt and clear data delimiting reduce success rates, but the design must assume some
injections succeed. The reliable controls are architectural: limit what tools and data the model can reach, separate
read from write, require approval for consequential actions, restrict egress, validate outputs, and monitor. Defence in
depth, not a single filter.

### 6. How would you design an agent that summarises inbound emails safely?

**Model answer:** The summariser gets the email content in clearly tagged data blocks and is told it is untrusted. It
has **no** tools that act (no send, no forward, no file access) because summarising does not need them. Output is
plain text, escaped before display, and any URLs are shown, not auto-fetched. If a later step needs action, a
separate component with its own authorisation and human confirmation performs it. I would red-team it with an
injection corpus and track the rate of instructions leaking into summaries.

### 7. What is the "lethal trifecta" style risk and how do you break it?

**Model answer:** It is the combination of access to private data, exposure to untrusted content and an ability to
communicate externally. With all three, injected instructions can read secrets and send them out, for example by
rendering an image URL containing the data. Break at least one leg: keep untrusted content away from agents with
sensitive access, remove or allowlist external communication (domain allowlists for fetch tools, no auto-loading of
remote images, egress proxies), or put human approval on outbound actions.

### 8. How do you test for prompt injection?

**Model answer:** Build an evaluation suite: a corpus of direct and indirect payloads (instruction overrides,
role-play, encoding tricks, hidden text in documents, malicious tool results) placed in every input channel the system
has. Define success criteria per case (no tool call, no data disclosure, no policy violation). Run it in CI on every
prompt, model or tool change, and in periodic manual red-team exercises. Measure attack success rate over time rather
than treating one pass as proof. See [lab 14](../19-hands-on-labs/lab-14-prompt-injection-testing/README.md).

## Agents, tools and permissions

### 9. What is excessive agency and how do you control it?

**Model answer:** Giving an LLM system more functionality, permissions or autonomy than its task needs, so a mistake or
manipulation causes outsized harm. Controls: minimal tool set; narrow tools instead of generic ones (a
`get_order_status` tool rather than raw SQL); least-privilege credentials per tool; actions performed with the end
user's permissions; approval gates for irreversible actions; rate and turn limits; and logging of every tool call.

### 10. Where should authorisation checks live in a tool-using agent?

**Model answer:** In the tool implementation and the systems behind it, keyed to the authenticated end user, never in
the prompt. The agent passes an identity context (for example a signed user token) that the tool verifies; the model
cannot supply or alter it. The tool then checks that this user may perform this action on this resource. This also
avoids the confused-deputy problem where the agent's broad service credentials do something the user could not.

### 11. How do you implement human-in-the-loop approval that cannot be bypassed by the model?

**Model answer:** The tool that performs the action refuses to run without an approval artefact created outside the
model's control: for example the agent proposes an action, the application shows the exact parameters to an
authorised human, and on approval issues a short-lived, single-use token bound to those parameters. The tool verifies
the token and parameters. Prompt text saying "ask before acting" is guidance only; the enforcement is in code. Approval
UIs must show precise effects, not model-written summaries alone.

### 12. How would you secure Claude Code for a development team?

**Model answer:** Managed settings for non-negotiable policy: deny rules for secret files (`Read(./.env)`), risky
commands and unapproved MCP servers; a model allowlist; no `bypassPermissions` except in disposable sandboxes. Shared
project settings for routine allow rules so prompt fatigue does not push people to over-approve. `PreToolUse` hooks for
policy checks and audit logging. Secrets in a manager, not in `CLAUDE.md`. Headless CI runs with tight
`--allowedTools`, `--max-turns` and no production credentials. Training on reviewing diffs and on injection risks
from repository content. See [09 · Permissions and settings](../09-claude-code/04-permissions-and-settings.md).

### 13. What risks do code execution and shell tools introduce, and how do you contain them?

**Model answer:** Arbitrary code execution, data access, lateral movement, resource abuse and exfiltration. Contain
with sandboxes (containers or VMs) without credentials, read-only mounts where possible, network egress restricted or
disabled, CPU/memory/time limits, ephemeral environments destroyed after use, and logging of commands. Server-hosted
code execution tools run in Anthropic's sandbox, but your own shell tools are your responsibility.

## MCP and supply chain

### 14. What are the main security risks of MCP servers?

**Model answer:** Malicious or compromised servers (supply chain), tool poisoning where descriptions carry hidden
instructions, rug pulls where a tool's definition changes after approval, over-broad OAuth scopes, token passthrough
and confused-deputy problems, local servers exposed on the network, and indirect injection via tool results. The spec
is explicit that hosts must obtain user consent before invoking tools and that tool annotations should be treated as
untrusted unless the server is trusted. See [12 · MCP server security](../12-ai-security/08-mcp-server-security.md).

### 15. What does the MCP authorization model require of an HTTP server?

**Model answer:** As of the 2026-07-28 revision: the server acts as an OAuth 2.1 resource server, publishes Protected
Resource Metadata (RFC 9728) so clients can find the authorization server, validates that access tokens were issued
for it as audience (clients send the RFC 8707 `resource` parameter), returns 401 with a `WWW-Authenticate` challenge
when unauthenticated and 403 `insufficient_scope` for step-up, and must not accept or pass through tokens meant for
other services. PKCE is required in the flow. stdio servers instead take credentials from the environment.

### 16. How do you govern which MCP servers employees can use?

**Model answer:** A registry of approved servers with owners, versions and security review status; pinned versions or
hashes; managed configuration in hosts that allows only registered servers; scopes reviewed per tool; monitoring of
tool calls; and a process for revoking a server quickly. For community servers, review code and dependencies and run
them in isolated environments with only the credentials they need.

### 17. What is AI supply chain risk beyond MCP?

**Model answer:** Third-party models and their provenance, fine-tuning datasets, embedding models, vector databases,
orchestration frameworks, plugins, prompt libraries and Skills that contain scripts, plus ordinary package
dependencies. Controls mirror software supply chain practice: approved sources, pinning, SBOMs extended to AI
components, signature or hash verification, dependency scanning and periodic review.

## Data protection and privacy

### 18. How do you prevent an assistant from leaking data across users?

**Model answer:** Enforce access control before data reaches the model: retrieval filtered by the user's
permissions, tools executed with the user's identity, tenant IDs enforced in code. Do not share conversation memory or
caches across users in ways that expose content. Keep secrets and other users' data out of prompts entirely. Test
with role-based scenarios and monitor for responses citing documents outside the user's entitlement.

### 19. What is system prompt leakage and why should it not be catastrophic?

**Model answer:** Users can often coax a model into revealing its system prompt. It becomes a problem only when the
prompt contains secrets, credentials, internal URLs or authorisation logic. Design assuming the prompt is public:
keep credentials in code and secret stores, enforce permissions in tools, and treat prompt confidentiality as a
nice-to-have, not a control.

### 20. How do you handle personal data in prompts for a regulated organisation?

**Model answer:** Classify data and decide which classes may be processed and where. Minimise: send only fields the
task needs; pseudonymise identifiers and re-identify in trusted code. Understand and document the provider's retention
and regional processing settings and contractual terms. Log with redaction. Run a data protection impact assessment
where required, and give users clear notices. Review regularly as features and models change.

### 21. How can an LLM application exfiltrate data without any obvious "send" tool?

**Model answer:** Through rendered Markdown images or links whose URLs carry data, through fetch tools that call
attacker URLs, through code execution with network access, through tool arguments to legitimate services the attacker
can read (creating a public ticket, for example), or simply by displaying data to the wrong user. Mitigate with
egress allowlists, not auto-rendering remote content, output scanning, and least-privilege tools.

## Output handling and integrity

### 22. Give examples of improper output handling and fixes

**Model answer:** Inserting model output into HTML without escaping (XSS); concatenating it into SQL (injection);
passing it to a shell (command injection); calling `eval` on generated code; following generated URLs server-side
(SSRF); trusting generated JSON without validation. Fixes: escape for the output context, parameterised queries,
argument arrays without a shell, sandboxed execution, URL allowlists and schema plus business-rule validation.

### 23. How do you protect a RAG knowledge base from poisoning?

**Model answer:** Control write access and require review for high-trust collections; track provenance and versions
of every document; scan new content for hidden text and instruction-like patterns; separate trusted internal content
from external or user-submitted content and label it in the prompt; monitor answers for sudden changes tied to
specific documents; and be able to remove a document and its chunks quickly.

## Governance, operations and incidents

### 24. What should an AI acceptable-use policy cover?

**Model answer:** Approved tools and accounts; data classes that may and may not be used; required human review for
certain outputs; disclosure of AI assistance where appropriate; prohibited uses (for example fully automated decisions
about people without oversight); intellectual property and confidentiality; security reporting; and training
requirements. It should be short, practical and backed by technical controls, not only rules.

### 25. How would you apply the NIST AI RMF to a new AI feature?

**Model answer:** Govern: assign ownership, policies and risk appetite. Map: document the context, users, intended and
foreseeable misuse, data flows and impacts. Measure: evaluate accuracy, robustness, bias, security (red-teaming) and
track metrics. Manage: implement controls, decide whether to deploy, monitor in production and respond to incidents.
The value is in making each step explicit and repeatable, with evidence an auditor can follow.

### 26. What should you log for an LLM system, and what should you not?

**Model answer:** Log request IDs, user and tenant IDs, model and prompt versions, tool calls with parameters and
outcomes, approval decisions, retrieved document IDs, stop reasons, token usage and latency, plus safety events such as
refusals and blocked actions. Avoid logging secrets and minimise raw personal data: redact or hash, restrict access to
logs, and set retention. Logs must be good enough to reconstruct an incident without becoming a new data leak.

### 27. Walk me through responding to a suspected prompt-injection incident in production

**Model answer:** Contain: disable the affected tool, connector or feature flag; rotate credentials the agent used if
misuse is possible. Preserve: export traces of the affected sessions, inputs, retrieved content and tool calls.
Assess: what actions ran, what data was exposed, which users. Eradicate: remove the malicious content, fix the
control that failed (permission, approval, egress rule). Recover with monitoring. Learn: add the payload to the
regression suite, update the threat model and communicate per policy and regulation.

### 28. A business leader asks you to "just turn off the safety stuff" because it blocks a legitimate workflow. How do you respond?

**Model answer:** Understand the workflow and the exact blocks first; often the fix is better context in the system
prompt, a different tool design or routing. Explain that model safeguards and our own controls exist for distinct
reasons, that bypassing provider safeguards is not an option, and that weakening our controls needs a risk
assessment with an accountable owner. Offer alternatives: scoped exceptions with compensating controls, human review
for the edge cases, or raising the use case with the provider through official channels. Document the decision.
