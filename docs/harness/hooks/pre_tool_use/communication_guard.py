#!/usr/bin/env python3
"""
PreToolUse hook — blocks unauthorized external communications.

Prevents autonomous agents from sending email, chat messages, SMS, or
calendar invitations without explicit human approval. Directly relevant
to executive assistant, chief-of-staff, legal, and customer-facing agents
where an unsanctioned message carries real reputational or legal risk.

Covers CLI tools, SMTP operations, and direct API calls to common
communication platforms. Not exhaustive — extend _CHECKS for your stack.

Exit 0: allow
Exit 2: block (stderr is fed back to the agent as the reason)
"""
import json
import re
import sys
from typing import List, Optional, Tuple

Pattern = re.Pattern

_CHECKS: List[Tuple[Pattern, str]] = [
    # --- Email: CLI tools ---
    (
        re.compile(r'\b(sendmail|mailx|mail|mutt|msmtp|swaks)\b'),
        "Blocked direct email command — sending email requires explicit human approval.\n"
        "Draft the message content and present it for review before any send operation.",
    ),
    # --- Email: SMTP in scripts ---
    (
        re.compile(r'\bsmtp(lib|\.SMTP|\.connect)\b', re.IGNORECASE),
        "Blocked SMTP operation — email sending requires explicit human approval.\n"
        "Draft the message content and present it for review before sending.",
    ),
    # --- Email: delivery APIs ---
    (
        re.compile(r'api\.(sendgrid|mailgun|postmark)\.com', re.IGNORECASE),
        "Blocked call to email delivery API.\n"
        "All outbound email must be reviewed and approved by a human before sending.",
    ),
    (
        re.compile(r'email\.us-\w+\.amazonaws\.com|ses\.amazonaws\.com', re.IGNORECASE),
        "Blocked AWS SES call.\n"
        "All outbound email must be reviewed and approved by a human before sending.",
    ),
    # --- Slack ---
    (
        re.compile(r'(hooks\.slack\.com|slack\.com/api/chat\.(post|update|delete))', re.IGNORECASE),
        "Blocked Slack API call that would post, edit, or delete a message.\n"
        "Draft the message and present it for human approval before posting.",
    ),
    # --- Microsoft Teams / Outlook ---
    (
        re.compile(r'graph\.microsoft\.com/.*/(sendMail|messages/send|events)', re.IGNORECASE),
        "Blocked Microsoft Graph call that would send email or create a calendar event.\n"
        "All outbound communications and calendar writes require human approval.",
    ),
    # --- Gmail / Google Calendar ---
    (
        re.compile(r'gmail\.googleapis\.com/.*messages/send', re.IGNORECASE),
        "Blocked Gmail API send.\n"
        "All outbound email requires human review and approval before sending.",
    ),
    (
        re.compile(r'calendar\.googleapis\.com/.*/events\b.*(POST|PATCH|DELETE)', re.IGNORECASE),
        "Blocked Google Calendar write operation.\n"
        "Creating, modifying, or deleting calendar events requires human approval.",
    ),
    # --- SMS ---
    (
        re.compile(r'api\.twilio\.com/.*Messages', re.IGNORECASE),
        "Blocked Twilio SMS API call.\n"
        "Sending SMS to external numbers requires explicit human approval.",
    ),
    (
        re.compile(r'api\.messagebird\.com|api\.vonage\.com|api\.bandwidth\.com', re.IGNORECASE),
        "Blocked SMS/voice API call.\n"
        "Sending messages to external numbers requires explicit human approval.",
    ),
    # --- Generic: any curl/wget POST to external domains with message-shaped payloads ---
    (
        re.compile(
            r'\b(curl|wget)\b.*-X\s*(POST|PATCH|PUT).*\b(subject|recipient|to|message|body)\b',
            re.IGNORECASE,
        ),
        "Blocked outbound HTTP write that appears to be sending a communication.\n"
        "Any operation that delivers a message to an external party requires human approval.",
    ),
]


def _blocked_reason(command: str) -> Optional[str]:
    for pattern, message in _CHECKS:
        if pattern.search(command):
            return message
    return None


def main() -> None:
    try:
        hook_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if hook_data.get('tool_name') != 'Bash':
        sys.exit(0)

    command = hook_data.get('tool_input', {}).get('command', '')
    if not command:
        sys.exit(0)

    reason = _blocked_reason(command)
    if reason:
        sys.stderr.write(f"[Harness: CommunicationGuard] {reason}\n")
        sys.exit(2)


if __name__ == '__main__':
    main()
