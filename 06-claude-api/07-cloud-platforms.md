# Cloud Platforms: AWS, Google Cloud and Microsoft Foundry

> **Level:** Intermediate → Advanced · **Time:** ~50 min · **Exam relevance:** CCAR-P D1, D3, D5

## In plain English

You can reach Claude models in more than one way. Besides calling Anthropic's own API directly, you can use Claude
through the major clouds, which many enterprises prefer because it fits their existing accounts, identity systems,
networking, billing commitments and compliance arrangements.

As of 2026-10-24 the main options are:

| Option | Who operates it | Billing | One-line summary |
|---|---|---|---|
| **Claude API** (first party) | Anthropic | Anthropic | Newest features first; Anthropic API keys or federated identity |
| **Claude Platform on AWS** | Anthropic, on AWS infrastructure | AWS Marketplace | Same API surface as first party, with AWS IAM authentication and AWS billing |
| **Claude in Amazon Bedrock** | AWS (partner-operated) | AWS | Claude inside Bedrock's ecosystem; a subset of features; `anthropic.`-prefixed model IDs |
| **Claude on Google Cloud (Vertex AI)** | Google (partner-operated) | Google Cloud | Claude inside Google Cloud; Google identity and billing |
| **Claude in Microsoft Foundry** | Anthropic-operated service, hosted on Azure or on Anthropic infrastructure | Azure Marketplace | Azure-native endpoints and Entra ID authentication |

All of them serve the same Claude models and essentially the same Messages API shape. They differ in **feature
availability, model ID format, authentication, data handling and pricing**. Anthropic's SDKs provide a dedicated client
class for each, so your application code changes very little.

## Why it matters

- Platform choice is an architecture decision with security, compliance, cost and capability consequences. It touches
  integration mechanism (CCAR-P-3.7), authentication and authorisation (CCAR-P-3.2), and regulatory compliance such as
  data residency (CCAR-P-5.4).
- Features are not identical everywhere. A design that relies on the Batches API, the Files API, server-side tools or
  Skills may not work unchanged on every platform.
- Enterprises often run multi-cloud, so knowing how to keep code portable is valuable.

## How it works

### Choosing a platform

| If you need... | Consider |
|---|---|
| The newest features as soon as they ship | Claude API, or Claude Platform on AWS (same-day parity, per Anthropic's docs) |
| AWS-native IAM and billing with full Anthropic API features | Claude Platform on AWS |
| Integration with Bedrock tooling (Bedrock guardrails, knowledge bases, existing Bedrock governance) | Claude in Amazon Bedrock |
| Google Cloud identity, VPC controls and billing | Vertex AI |
| Azure identity (Entra ID), Azure networking and Azure Marketplace billing | Microsoft Foundry |
| Specific data-residency guarantees | Compare each platform's regional options; on the Claude API, `inference_geo` offers only US-only or global inference (as of 2026-10-24); for other regions, use a platform's regional endpoint or inference profile |

### Feature availability snapshot (as of 2026-10-24)

Feature support changes frequently. Always confirm in Anthropic's
[features overview](https://platform.claude.com/docs/en/build-with-claude/overview) and the platform pages.

| Feature | Claude API | Platform on AWS | Bedrock | Vertex AI | Foundry |
|---|:---:|:---:|:---:|:---:|:---:|
| Messages, streaming, tool use, vision, PDFs | Yes | Yes | Yes | Yes | Yes |
| Structured outputs, adaptive thinking and effort | Yes | Yes | Yes | Yes | Yes |
| Prompt caching | Yes | Yes | Yes (legacy integration: explicit breakpoints only) | Yes | Yes |
| Citations, token counting | Yes | Yes | Yes | Yes | Yes |
| Message Batches API | Yes | Yes | No | No | No |
| Files API | Yes | Yes | No | No | Anthropic-hosted only (beta) |
| Models API | Yes | Yes | No | No | No |
| Web search | Yes | Yes | No | Basic version | Yes (basic version when hosted on Azure) |
| Code execution, Agent Skills | Yes | Yes | No | No | Anthropic-hosted only |
| Server-side refusal fallbacks | Beta | Beta | No (use SDK middleware) | No (use SDK middleware) | No (use SDK middleware) |
| `inference_geo` data residency parameter | Yes | Yes | No | No | No (use deployment type) |
| Managed Agents | Beta | Beta | No | No | No |

### Client classes (Python)

Each platform has its own client class. After construction, you use the same `messages.create()` and
`messages.stream()` methods. Do not point the first-party `Anthropic()` client at a cloud endpoint with a
`base_url` override; use the platform client, which handles authentication and URL formats.

| Platform | Install | Client | Model ID format | Authentication |
|---|---|---|---|---|
| Claude API | `pip install anthropic` | `anthropic.Anthropic()` | `claude-opus-5-5` | API key or federated identity |
| Claude Platform on AWS | `pip install "anthropic[aws]"` | `anthropic.AnthropicAWS()` | `claude-opus-5-5` (no prefix) | AWS credentials (SigV4) or short-term API keys; needs `AWS_REGION` and `ANTHROPIC_AWS_WORKSPACE_ID` |
| Claude in Amazon Bedrock | `pip install "anthropic[bedrock]"` | `anthropic.AnthropicBedrockMantle(aws_region=...)` | `anthropic.claude-opus-5-5` | AWS credentials or Bedrock bearer tokens |
| Vertex AI | `pip install "anthropic[vertex]"` | `anthropic.AnthropicVertex(project_id=..., region=...)` | `claude-opus-5-5` (no prefix for current models) | Google Application Default Credentials |
| Microsoft Foundry | `pip install anthropic` (plus `azure-identity` for Entra ID) | `anthropic.AnthropicFoundry(resource=..., api_key=...)` | Your deployment name (defaults to the model ID) | Foundry API key or Entra ID token provider |

Notes:

- **Bedrock has two integrations.** The newer "Claude in Amazon Bedrock" endpoint serves the Messages API shape and
  uses the `AnthropicBedrockMantle` client. The legacy `AnthropicBedrock` client uses Bedrock's `InvokeModel` /
  `Converse` APIs with ARN-versioned model IDs and inference-profile prefixes (`global.`, `us.`, `eu.`). Prefer the
  newer client for new code on current models.
- **Vertex AI regions.** `region` can be `"global"` (recommended for availability), a multi-region such as `"us"` or
  `"eu"`, or a specific region. Anthropic's docs now refer to this offering as Claude Models on Google Cloud.
- **Foundry deployments.** The `model` parameter is the **deployment name** you created in the Foundry portal.
  Deployments can be hosted on Azure (inference stays within Azure) or on Anthropic infrastructure (wider feature set).

### Conceptual differences that matter to architects

| Dimension | What to check |
|---|---|
| Data processing and residency | Where inference runs, regional versus global endpoints, contractual terms (for example Foundry's Hosted on Azure option keeps prompts within Azure) |
| Identity | Reuse of cloud IAM, Entra ID or Google identity; short-lived credentials; no long-lived Anthropic keys |
| Networking | Private connectivity options (VPC endpoints, private networking) offered by each cloud |
| Quotas and rate limits | Managed per platform; Foundry, for example, does not return Anthropic's rate-limit headers |
| Pricing | Partner platforms price separately; some charge a premium for regional endpoints |
| Release timing | Partner-operated platforms can lag first-party feature releases |
| Observability | Cloud-native logging (CloudWatch, Cloud Logging, Azure Monitor) and request IDs |

## Example

*Contoso Health* (fictional) runs its main workloads on AWS but has one team on Azure. It wraps client construction in a
small factory so application code is identical across platforms, and keeps platform-specific settings in environment
variables.

```python
import os

import anthropic

PLATFORM = os.environ.get("CLAUDE_PLATFORM", "anthropic")


def make_client():
    """Return a client for the configured platform. Credentials come from the environment."""
    if PLATFORM == "anthropic":
        return anthropic.Anthropic()                                   # ANTHROPIC_API_KEY or federation
    if PLATFORM == "aws":
        return anthropic.AnthropicAWS()                                # AWS_REGION + ANTHROPIC_AWS_WORKSPACE_ID
    if PLATFORM == "bedrock":
        return anthropic.AnthropicBedrockMantle(aws_region=os.environ["AWS_REGION"])
    if PLATFORM == "vertex":
        return anthropic.AnthropicVertex(project_id=os.environ["GCP_PROJECT_ID"],
                                         region=os.environ.get("GCP_REGION", "global"))
    if PLATFORM == "foundry":
        return anthropic.AnthropicFoundry(api_key=os.environ["ANTHROPIC_FOUNDRY_API_KEY"],
                                          resource=os.environ["ANTHROPIC_FOUNDRY_RESOURCE"])
    raise ValueError(f"Unknown CLAUDE_PLATFORM {PLATFORM!r}")


MODEL_IDS = {   # same model, platform-specific identifiers
    "anthropic": "claude-opus-5-5",
    "aws": "claude-opus-5-5",
    "bedrock": "anthropic.claude-opus-5-5",
    "vertex": "claude-opus-5-5",
    "foundry": os.environ.get("FOUNDRY_DEPLOYMENT", "claude-opus-5-5"),
}

client = make_client()
response = client.messages.create(
    model=MODEL_IDS[PLATFORM],
    max_tokens=1000,
    messages=[{"role": "user", "content": "Summarise our hand-hygiene audit procedure in three bullets."}],
)
if response.stop_reason == "end_turn":
    print(next(b.text for b in response.content if b.type == "text"))
```

> **Cost:** requires credits or billing on the chosen platform (live mode). Prices differ between platforms.

A factory hides construction differences, but not feature differences. Contoso's code checks a capability table
before using Batches, the Files API or server tools, and fails clearly if a platform lacks them.

## Enterprise use case

*Woodgrove Bank* (fictional) had three requirements: no long-lived third-party API keys, inference within its approved
cloud regions, and billing through its existing cloud commitment. Its architects compared options in an architecture
decision record (see [architecture decision records](../13-enterprise-ai-architecture/07-architecture-decision-records.md)):

- The direct Claude API offered the newest features and the `inference_geo` control but needed a separate vendor
  contract and billing.
- Claude Platform on AWS met the identity and billing requirements with full feature parity, including the Batches
  and Files APIs the team needed for nightly document processing.
- Bedrock fitted their existing Bedrock governance but lacked the Batches and Files APIs the design relied on.

They chose Claude Platform on AWS for the document-processing system and kept a small Bedrock deployment for a team
already using Bedrock knowledge bases. The decision record lists the features each design depends on, so a future
platform change can be assessed quickly.

## Common mistakes

- **Assuming feature parity.** Check the features overview for every feature you depend on.
- **Using the wrong model ID format.** Bedrock needs the `anthropic.` prefix; Foundry uses deployment names; Platform
  on AWS and Vertex use bare IDs for current models.
- **Overriding `base_url` on the first-party client** instead of using the platform client class.
- **Confusing Claude Platform on AWS with Bedrock.** They coexist and differ in operator, features and model IDs.
- **Mixing credentials.** For example, an `ANTHROPIC_API_KEY` in the environment being sent to a cloud endpoint.
  Pass platform credentials explicitly.
- **Forgetting regional pricing.** Some regional endpoints carry a premium.

## Security considerations

- **Prefer platform-native, short-lived identity**: IAM roles, Entra ID managed identities, Google service accounts.
- **Least privilege**: grant only the inference permissions a workload needs; separate roles for administration.
- **Data handling**: read each platform's data-processing terms; confirm logging settings (for example cloud invocation
  logging) do not store prompts in places your policy forbids, or do store them where audit requires.
- **Network controls**: use private endpoints where available and restrict egress.
- **Consistent guardrails**: input checks, output validation and monitoring must be applied on every platform you use,
  not just the primary one (see [enterprise deployment controls](../12-ai-security/14-enterprise-deployment-controls.md)).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 400 for a feature that works on the Claude API | Feature not supported on this platform | Check the features overview; redesign or switch platform for that workload |
| 404 or "model not found" on Bedrock | Missing `anthropic.` prefix, wrong region, or model access not enabled | Use the correct ID and region; enable model access in the AWS console |
| "Deployment not found" on Foundry | Using the model ID instead of your custom deployment name | Pass the deployment name |
| Error constructing `AnthropicAWS` | `AWS_REGION` or workspace ID missing | Set both; there is no default |
| 403 on Claude Platform on AWS | Wrong workspace ID or missing IAM action | Check the workspace ID and IAM policy |
| 401 on Foundry with Entra ID | Expired token or missing RBAC role | Use a token provider; assign a Foundry user role |

## Check your understanding

1. What is the main difference between Claude Platform on AWS and Claude in Amazon Bedrock?
2. Why should you use `AnthropicVertex` rather than `Anthropic(base_url=...)` for Vertex AI?
3. Name two features you should verify before moving a design from the Claude API to Bedrock.
4. On Microsoft Foundry, what value do you pass as `model`?

<details>
<summary>Answers</summary>

1. Claude Platform on AWS is operated by Anthropic with the same API surface and same-day feature parity, using AWS
   authentication and billing and bare model IDs. Bedrock is operated by AWS, offers a subset of features, and uses
   `anthropic.`-prefixed model IDs.
2. The platform client handles Google authentication (Application Default Credentials), URL construction and request
   format differences; a base URL override on the first-party client does not.
3. Any two of: Message Batches API, Files API, server-side tools (web search, code execution), Agent Skills, automatic
   prompt caching, server-side fallbacks, the Models API.
4. The deployment name you created in the Foundry portal (which defaults to the model ID).

</details>

## Further reading

- [Features overview](https://platform.claude.com/docs/en/build-with-claude/overview) (Anthropic docs, platform availability)
- [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) (Anthropic docs)
- [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock) (Anthropic docs)
- [Claude on Vertex AI](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai) (Anthropic docs)
- [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry) (Anthropic docs)
- [Integration patterns](../13-enterprise-ai-architecture/04-integration-patterns.md) in this repository

<!-- page-nav:start -->
---

[← Previous: Errors, Rate Limits and Retries](06-errors-rate-limits-retries.md) · [Module overview](README.md) · [Next: Token Counting and Cost →](08-token-counting-and-cost.md)
<!-- page-nav:end -->
