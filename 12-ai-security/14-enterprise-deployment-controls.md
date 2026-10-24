# Enterprise Deployment Controls

> **Level:** Intermediate · **Time:** ~40 min · **Exam relevance:** CCAR-P D5 (5.4), CCAR-P D7 (7.1), CCAO-F D6 (6.2, 6.3)

## In plain English

Everything earlier in this module is about controls you build into your own application. This page is about the
controls Anthropic's products give administrators: who can sign in, how accounts are provisioned and removed, how long
data is kept, where inference runs, which networks can reach the service, and which settings users can or cannot
change.

The aim is to separate what is actually offered from what people assume is offered. Every feature listed here was
checked against Anthropic's official documentation on 2026-10-24. Availability depends on plan and platform and
changes over time, so confirm against the linked pages and your contract before you design around a control.

## Why it matters

- Security and procurement reviews ask for these controls by name: SSO, SCIM, audit logs, retention, encryption keys,
  residency, IP restrictions.
- Choosing the wrong surface (for example a consumer plan for regulated data) can make an otherwise good design
  non-compliant.
- CCAR-P-7.1 covers configuring Claude tools for teams, and CCAR-P-5.4 covers regulatory compliance.

## How it works

### Map controls to surfaces

| Surface | Who administers | Main control points |
|---|---|---|
| Claude apps on Team and Enterprise plans (claude.ai, desktop, mobile) | Organisation admins | Identity (SSO, JIT, SCIM), roles, retention, audit logs, Compliance API, connectors, network restrictions |
| Claude API (Claude Console) | Organisation and workspace admins | Workspaces, API keys, spend and rate limits, data-retention arrangements, Admin API, workload identity |
| Claude Code | Admins via managed settings, plus Console or plan admin | Managed settings and permissions, managed MCP configuration, sandboxing, monitoring |
| Claude on cloud platforms (Amazon Bedrock, Google Cloud, Microsoft Foundry) and Claude Platform on AWS | Your cloud account administrators | The cloud's IAM, networking, logging and regional controls; data processing terms depend on the platform |

### Claude Enterprise plan controls

Anthropic's help centre article [What is the Enterprise plan?](https://support.claude.com/en/articles/9797531-what-is-the-enterprise-plan)
and the Enterprise security and compliance collection list these administrative controls (as of 2026-10-24):

| Control | What it gives you |
|---|---|
| SSO, just-in-time provisioning and SCIM | Central authentication through your identity provider; automated provisioning and de-provisioning (documented in the help centre's identity management collection; confirm plan availability) |
| Audit logs | Records of user actions, system events and data access |
| Custom data retention controls | Organisation-defined retention for chats, files and projects |
| Compliance API | Programmatic access to activity logs, chat histories and file content, filterable by user and time range, for compliance tooling |
| Analytics API | Aggregated engagement and adoption metrics |
| Customer-managed encryption keys (CMEK) | Use a key in your own cloud provider to protect chats, projects and files |
| US-only inference | Keep the organisation's inference in the United States |
| Spend limits | Organisation and per-user limits |
| HIPAA-ready configuration | Eligible organisations can enable it and accept a business associate agreement |
| IP allowlisting | Restrict access to Claude to approved IP ranges |
| Tenant Restrictions | Network-level control to stop users signing in to organisations other than yours from your network |
| Connectors administration | Control workplace connectors such as Google Drive, Gmail, GitHub, Microsoft 365 and Slack |

The last three items come from article titles in the Enterprise security and compliance collection ("Restrict access
to Claude with IP allowlisting", "Enforce network-level access control with Tenant Restrictions"); read those
articles for configuration details and plan requirements.

### Claude API controls

| Control | Details (verified 2026-10-24) |
|---|---|
| Workspaces | Separate API keys, members, and spend and rate limits per workspace; organisation-wide limits still apply |
| Spend limits | Per-tier monthly caps, plus your own lower limits for the organisation and for workspaces |
| Rate limits | RPM, input and output tokens per minute per model class; readable via the Rate Limits API |
| Admin API | Manage members, invites, workspaces, API keys, service accounts and federation rules programmatically with an admin credential |
| Workload identity federation | Exchange your platform's identity token for short-lived credentials instead of long-lived API keys |
| Inference geography | The `inference_geo` request parameter (supported on Opus 4.6 / Sonnet 4.6 and later) controls where inference runs, with `"us"` or `"global"` as the only values as of 2026-10-24; `usage.inference_geo` reports it. For other regions, use a cloud platform's regional endpoint |
| Usage and cost reporting | Usage and Cost Admin API; Console usage export by key and model |
| OpenTelemetry | SDK and API tracing (beta) to your backend, metadata-only by default |

### Data retention, ZDR and HIPAA on the API

Anthropic's [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) page
(checked 2026-10-24) states:

- Only what is technically necessary for each feature is retained, and conversation content (prompts and outputs)
  is not retained by default. The exception is **Covered Models**, which require 30-day retention. Standard
  commercial retention policies outside the ZDR and HIPAA arrangements are documented separately on Anthropic's
  privacy pages. Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5 and Claude
  Mythos 5 are listed as requiring 30-day retention and are not available under ZDR unless expressly authorised.
- **Zero data retention (ZDR)** is arranged with Anthropic's sales team and enabled per organisation. Under ZDR,
  Anthropic does not store prompts or responses at rest after the response is returned, for eligible features of the
  Messages and Token Counting APIs listed in the page's feature-eligibility table. Some features that use
  `/v1/messages`, such as code execution, are not covered.
- ZDR applies to Claude Code used with API keys from a commercial organisation (metrics logging, if enabled, is
  exempt). Claude Code on Claude Enterprise has a separate ZDR offering for qualified accounts.
- ZDR does **not** cover the Claude Console (including the playground), Claude Managed Agents (session transcripts
  persist until deleted), consumer plans, the Team and Enterprise product interfaces, third-party integrations, or
  flagged content and legal holds. CORS (direct browser calls) is not supported for ZDR organisations.
- **HIPAA readiness** for the API is available with a signed BAA and a HIPAA-enabled organisation, for eligible
  features.
- Who processes your data depends on the route. On Amazon Bedrock, and for Claude models on Google Cloud that Google
  manages, the cloud provider is the processor, so its retention and compliance terms apply. On Google Cloud offerings
  that Anthropic manages, on Claude Platform on AWS and on Microsoft Foundry, Anthropic is the processor (checked
  2026-10-24 against Anthropic's [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) page).

Design implication: build a feature-by-feature data-flow table. A pipeline that is ZDR-eligible for plain Messages
calls may lose that property the moment you add a stateful or file-based feature.

### Claude Code organisational controls

Per [Claude Code security](https://code.claude.com/docs/en/security) (checked 2026-10-24):

- **Managed settings** enforce organisational standards and permission rules that users cannot override.
- **Permission modes**: organisations can turn auto mode off; explicit allow and deny rules apply in every mode.
- **Managed MCP configuration** restricts which MCP servers can run.
- **Sandboxing** isolates bash commands at the filesystem and network level; the whole process can run in a sandbox
  runtime or dev container.
- **Monitoring** via OpenTelemetry metrics, and `ConfigChange` hooks to audit or block settings changes mid-session.
- **Cloud sessions** run in isolated VMs with limited network access by default, server-side GitHub credentials,
  push restrictions and audit logging.

See [Claude Code team rollout](../09-claude-code/08-team-rollout.md) for a rollout plan.

### Network controls you own

- Route all API traffic from servers through an egress proxy with an allow-list for Anthropic endpoints, so you can
  monitor volume and block unapproved destinations.
- Never call the API from browsers or mobile apps with embedded keys; use a backend.
- On cloud platforms, use the cloud's private networking and IAM features as documented by that provider.
- Combine IP allowlisting (for the Claude apps) with your corporate network controls and Tenant Restrictions to stop
  data going to personal accounts.

## Example

A deployment-readiness check that turns this page into a repeatable gate. Fill the YAML-free dictionary from your
configuration management database and fail the pipeline on gaps.

```python
"""enterprise_controls_check.py - check a deployment's control posture against its data class."""
CONTROL_REQUIREMENTS = {
    "public":   {"sso"},
    "internal": {"sso", "scim", "audit_logs", "workspace_isolation", "spend_limits"},
    "personal": {"sso", "scim", "audit_logs", "workspace_isolation", "spend_limits",
                 "retention_policy_set", "egress_proxy", "no_client_side_keys"},
    "phi":      {"sso", "scim", "audit_logs", "workspace_isolation", "spend_limits",
                 "retention_policy_set", "egress_proxy", "no_client_side_keys",
                 "hipaa_ready_org", "baa_signed", "features_checked_against_eligibility_table"},
}

def check(deployment: dict) -> list[str]:
    required = CONTROL_REQUIREMENTS[deployment["highest_data_class"]]
    missing = sorted(required - set(deployment["controls"]))
    problems = [f"missing control: {c}" for c in missing]
    if deployment.get("requires_zdr") and deployment.get("uses_stateful_features"):
        problems.append("ZDR required but deployment uses features outside ZDR scope; review eligibility table")
    return problems

if __name__ == "__main__":
    print(check({
        "name": "clinical-notes-summariser",
        "highest_data_class": "phi",
        "controls": ["sso", "scim", "audit_logs", "workspace_isolation", "spend_limits",
                     "retention_policy_set", "egress_proxy", "no_client_side_keys", "hipaa_ready_org"],
        "requires_zdr": True,
        "uses_stateful_features": True,
    }))
```

## Enterprise use case

*Contoso Health* deploys Claude in three ways:

1. **Claude Enterprise for 4,000 staff**: SSO with SCIM from its identity provider, IP allowlisting to corporate
   egress addresses, Tenant Restrictions on the corporate proxy, custom retention of 90 days, audit logs and the
   Compliance API feeding the security information and event management (SIEM) platform, HIPAA-ready configuration
   with a BAA, and connectors limited to the corporate Microsoft 365 tenant.
2. **Claude API for a clinical-notes summariser**: a dedicated workspace with its own spend and rate limits, HIPAA
   readiness for eligible features, workload identity federation instead of static keys, an egress proxy, and a design
   review that confirmed every feature used is in the eligibility table.
3. **Claude Code for 120 engineers**: managed settings with deny rules for secret files, sandboxing on, managed MCP
   allow-list, auto mode disabled for repositories with production access, and OpenTelemetry metrics to the
   engineering observability stack.

## Common mistakes

- Assuming "enterprise" means every feature is ZDR-eligible.
- Letting staff use personal consumer accounts for work data because no network control blocks them.
- Using one Console workspace and API key for every application.
- Enabling connectors organisation-wide without reviewing what data they expose.
- Designing around a feature without checking plan, platform and regional availability.

## Security considerations

- Retention settings and ZDR do not remove your own obligations for logs and copies you keep.
- Review admin roles regularly: Console organisation admins and Claude Enterprise owners hold powerful rights.
- Treat Compliance API access as highly privileged; it can read conversation content.
- When using cloud platforms, the cloud provider's controls and terms apply; validate feature parity for the controls
  you need.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Browser app calls fail after ZDR enablement | CORS not supported for ZDR organisations | Route calls through your backend |
| A model returns a 400 for a ZDR organisation | The model requires 30-day retention (Covered Model) | Use a model available under your arrangement, or discuss with Anthropic |
| De-provisioned staff still have access | SCIM not configured or not syncing | Configure SCIM and monitor sync errors |
| Usage appears in the wrong cost centre | Shared keys across teams | One workspace and key per application or team |

## Check your understanding

1. Name four administrative controls available on the Claude Enterprise plan.
2. Which Anthropic surfaces does the API ZDR arrangement explicitly not cover?
3. Why must browser-based applications in a ZDR organisation call Claude through a backend?
4. Which Claude Code feature lets an organisation stop users from overriding permission rules?

<details>
<summary>Answers</summary>

1. Any four of: SSO/JIT/SCIM, audit logs, custom data retention, Compliance API, Analytics API, CMEK, US-only
   inference, spend limits, HIPAA-ready configuration, IP allowlisting, Tenant Restrictions.
2. The Claude Console (including the playground), Claude Managed Agents, consumer plans, the Team and Enterprise
   product interfaces (except the separate Claude Code on Enterprise offering), third-party integrations, and flagged
   content or legal holds.
3. CORS is not supported for ZDR organisations, and in any case API keys must never be exposed client-side.
4. Managed settings.

</details>

## Further reading

- Anthropic: [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)
- Anthropic: [What is the Enterprise plan?](https://support.claude.com/en/articles/9797531-what-is-the-enterprise-plan)
- Anthropic: [Rate limits](https://platform.claude.com/docs/en/api/rate-limits),
  [Workspaces](https://platform.claude.com/docs/en/manage-claude/workspaces),
  [Admin API](https://platform.claude.com/docs/en/manage-claude/admin-api)
- Anthropic: [Claude Code security](https://code.claude.com/docs/en/security) and
  [settings](https://code.claude.com/docs/en/settings)
- Anthropic: [Trust Center](https://trust.anthropic.com)
- In this repository: [cloud platforms](../06-claude-api/07-cloud-platforms.md),
  [team rollout](../09-claude-code/08-team-rollout.md),
  [reference architectures](../13-enterprise-ai-architecture/03-reference-architectures.md),
  [Lab 20](../19-hands-on-labs/lab-20-secure-enterprise-architecture/README.md)

<!-- page-nav:start -->
---

[← Previous: Human Oversight](13-human-oversight.md) · [Module overview](README.md) · [Next module: Module 13: Enterprise AI Architecture →](../13-enterprise-ai-architecture/README.md)
<!-- page-nav:end -->
