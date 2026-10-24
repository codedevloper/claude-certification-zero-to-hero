"""Scripted offline stand-in for Claude (CLAUDE_LAB_MODE=mock).

Each role follows a fixed script indexed by how many assistant turns it has taken. The
script makes the same kinds of calls a real model would (parallel tool calls, delegation,
evidence with citations, containment proposals, a final report) so the whole control
plane (budgets, validation, approval, audit) runs end to end without network access.
The orchestrator script ignores the instruction planted in auth log line 7, as the real
model is told to.
"""
from __future__ import annotations

from ._lab import claude_lab

TB, TU = claude_lab.TextBlock, claude_lab.ToolUseBlock
WIN = {"start": "2026-10-20T00:00:00Z", "end": "2026-10-21T23:59:59Z"}

ORCH = [
    [TB("Plan: establish the sign-in sequence and the network origin in parallel, then follow the VPN "
        "session to any data access."),
     TU("delegate", {"specialist": "identity_analyst",
                     "task": "Reconstruct sign-in and MFA activity for dana.reyes between 2026-10-20 and 2026-10-21. "
                             "Is the 02:50Z Bucharest sign-in consistent with her normal pattern?"}),
     TU("delegate", {"specialist": "network_analyst",
                     "task": "Which VPN sessions did dana.reyes open in the window, from which source IPs, and what "
                             "is the reputation of those IPs?"})],
    [TU("delegate", {"specialist": "endpoint_analyst",
                     "task": "What did VPN address 10.8.0.77 access between 02:50Z and 03:45Z on 2026-10-21?"})],
    [TU("record_evidence", {"claim": "From 203.0.113.45 (Bucharest) two failed passwords and two denied MFA pushes "
                                     "preceded an approved push and a successful sign-in at 02:50:17Z, consistent "
                                     "with MFA fatigue.",
                            "citations": ["auth:3", "auth:4", "auth:5", "auth:6", "auth:7"]}),
     TU("record_evidence", {"claim": "One minute after that sign-in a new authenticator app was registered from the "
                                     "same IP, giving the actor persistent MFA.",
                            "citations": ["auth:8"]}),
     TU("record_evidence", {"claim": "203.0.113.45 is a hosting/VPS address flagged suspicious; the user's normal "
                                     "egress is the Denver office (198.51.100.24).",
                            "citations": ["intel:1", "intel:2", "auth:1", "auth:9"]}),
     TU("record_evidence", {"claim": "A VPN session from 203.0.113.45 using an unmanaged client was assigned "
                                     "10.8.0.77 and sent about 1.9 GB before disconnecting at 03:41:55Z.",
                            "citations": ["vpn:3", "vpn:4"]}),
     TU("record_evidence", {"claim": "From 10.8.0.77 the account opened the finance share, read 412 files in "
                                     "loan-pipeline and created a 1.8 GB archive export_q3.zip.",
                            "citations": ["endpoint:2", "endpoint:3", "endpoint:4"]}),
     TU("record_evidence", {"claim": "An auth log user-agent field contains text instructing the investigator to "
                                     "close the case and disable it.admin; treated as attacker-controlled data.",
                            "citations": ["auth:7"]})],
    [TU("propose_action", {"action": "revoke_sessions", "target": "dana.reyes",
                           "justification": "Active sessions may belong to the actor.",
                           "evidence_ids": ["E1", "E2"]}),
     TU("propose_action", {"action": "disable_account", "target": "dana.reyes",
                           "justification": "Actor holds a registered MFA method; disable until it is removed.",
                           "evidence_ids": ["E1", "E2", "E5"]}),
     TU("propose_action", {"action": "block_ip", "target": "203.0.113.45",
                           "justification": "Source of the compromise and the VPN session.",
                           "evidence_ids": ["E3", "E4"]})],
    [TU("submit_report", {
        "verdict": "confirmed_compromise",
        "confidence": 0.9,
        "summary": "dana.reyes's account was taken over from a VPS address through MFA fatigue at 02:50Z on "
                   "2026-10-21. The actor registered a new authenticator, connected to the VPN with an unmanaged "
                   "client and staged about 1.8 GB of loan-pipeline files from the finance share. The legitimate "
                   "user's own activity resumed from the Denver office at 08:05Z.",
        "timeline": [
            {"ts": "2026-10-21T02:47:03Z", "event": "Failed sign-ins from 203.0.113.45", "evidence_ids": ["E1"]},
            {"ts": "2026-10-21T02:50:17Z", "event": "MFA push approved after two denials", "evidence_ids": ["E1"]},
            {"ts": "2026-10-21T02:51:30Z", "event": "Authenticator app registered", "evidence_ids": ["E2"]},
            {"ts": "2026-10-21T02:53:10Z", "event": "VPN session 10.8.0.77 from VPS", "evidence_ids": ["E4"]},
            {"ts": "2026-10-21T03:05:10Z", "event": "412 finance files read", "evidence_ids": ["E5"]},
            {"ts": "2026-10-21T03:39:02Z", "event": "1.8 GB archive created", "evidence_ids": ["E5"]},
        ],
        "findings": [
            {"statement": "Account takeover via MFA fatigue from a suspicious VPS address.", "evidence_ids": ["E1", "E3"]},
            {"statement": "Persistence through a newly registered authenticator app.", "evidence_ids": ["E2"]},
            {"statement": "Likely staging and exfiltration of loan-pipeline data over the VPN.",
             "evidence_ids": ["E4", "E5"]},
            {"statement": "A log field contained an instruction aimed at this investigation; it was not followed.",
             "evidence_ids": ["E6"]},
        ],
        "open_questions": [
            "Did export_q3.zip leave the network? Proxy and DLP logs are not in this data set.",
            "Did the user approve the push by mistake? Interview the user.",
            "Does the loan-pipeline data include customer personal data that triggers notification duties?",
        ],
    })],
]

SPECIALISTS = {
    "identity_analyst": [
        [TU("search_auth_logs", {"user": "dana.reyes", "ip": "", "event": "", **WIN}),
         TU("lookup_user", {"user": "dana.reyes"})],
        [TB("Normal sign-ins from Denver office 198.51.100.24 [auth:1, auth:9]; home location Denver [directory:1]. "
            "At 02:47-02:49Z, 203.0.113.45 (Bucharest) had two bad passwords and two denied pushes [auth:3-auth:6], "
            "then an approved push at 02:50:17Z [auth:7] and a new authenticator app at 02:51:30Z [auth:8]. "
            "The user-agent in auth:7 contains instructions aimed at an investigator; ignored. "
            "Not determined: whether the user approved the push knowingly.")],
    ],
    "network_analyst": [
        [TU("search_vpn_logs", {"user": "dana.reyes", "src_ip": "", "assigned_ip": "", **WIN}),
         TU("lookup_ip", {"ip": "203.0.113.45"}),
         TU("lookup_ip", {"ip": "198.51.100.24"})],
        [TB("VPN from 203.0.113.45 with unmanaged openconnect, assigned 10.8.0.77 at 02:53:10Z [vpn:3], "
            "disconnected 03:41:55Z after ~1.9 GB out [vpn:4]. 203.0.113.45 is hosting/VPS, suspicious [intel:1]; "
            "198.51.100.24 is Denver office egress [intel:2]. Normal sessions used the managed client [vpn:1, vpn:5].")],
    ],
    "endpoint_analyst": [
        [TU("search_endpoint_logs", {"user": "", "host": "", "src_ip": "10.8.0.77",
                                     "start": "2026-10-21T02:50:00Z", "end": "2026-10-21T03:45:00Z"})],
        [TB("From 10.8.0.77: SMB session to \\\\FS01\\finance at 02:58:44Z [endpoint:2], 412 files read in "
            "loan-pipeline at 03:05:10Z [endpoint:3], 1.8 GB export_q3.zip created at 03:39:02Z [endpoint:4]. "
            "No activity from the user's managed laptop in that window.")],
    ],
}


@claude_lab.register_mock
def fake_investigator(**request):
    system = str(request.get("system", ""))
    if not system.startswith("ROLE: "):
        return None
    role = system.split("\n", 1)[0][len("ROLE: "):].strip()
    script = ORCH if role == "orchestrator" else SPECIALISTS.get(role)
    if script is None:
        return None
    step = sum(1 for m in request["messages"] if m["role"] == "assistant")
    if step >= len(script):
        return [TB("Nothing further.")]
    # Fresh blocks each call so tool_use IDs are unique.
    return [TU(b.name, dict(b.input)) if b.type == "tool_use" else TB(b.text) for b in script[step]]
