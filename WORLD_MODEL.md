# WORLD_MODEL.md
#
# Operational knowledge base for this project.
# Encodes what the world looks like from here —
# vendor capabilities, infrastructure topology,
# failure patterns, known edge cases.
#
# Unlike AGENTS.md (which governs agent behaviour),
# this file grounds agents in operational reality.
# Agents read both: AGENTS.md to know what to do,
# WORLD_MODEL.md to know what they are operating on.
#
# This file is project-owned. The framework never
# modifies it. Every resolved incident that reveals
# new knowledge must update this file before closing.

---

## Infrastructure Topology

# REPLACE: Declare your nodes, roles, and connections.
# Example:
#
# nodes:
#   superman:
#     role:    primary application host
#     vendor:  Hetzner
#     ip:      188.34.139.77
#     os:      Ubuntu 24.04 LTS
#
#   batman:
#     role:    database host
#     vendor:  Hetzner
#     ip:      144.76.163.247
#     os:      Ubuntu 24.04 LTS
#
# network:
#   vpn:     Tinc (plutonet)
#   colo:    rafael.pluio.net — Toronto primary

---

## Vendor Capabilities

# REPLACE: Declare what each vendor can do that
# agents should know about — especially non-obvious
# recovery tools and access methods.
# Example:
#
# hetzner:
#   robot_console:  https://robot.hetzner.com
#   virtual_kvm:    available via Robot console
#                   → Server → KVM console
#   rescue_mode:    available via Robot console
#                   → Server → Rescue
#   support:        https://support.hetzner.com
#   note: >
#     Hot-swap of physical disk may leave boot stack
#     broken. Virtual KVM required to diagnose and
#     fix at boot loader level.

---

## Failure Patterns

# Structured knowledge extracted from resolved incidents.
# Format per pattern:
#
# ### Pattern: {short name}
#   Vendor:      {vendor or 'any'}
#   Layer:       {Hardware | Boot | OS | Network |
#                 Service | Application | Auth}
#   Symptoms:    {observable signals at agent layer}
#   Cause:       {what actually caused it}
#   Diagnosis:   {how to confirm the cause}
#   Tool:        {what accesses the right layer}
#   Procedure:   {steps that resolve it}
#   Discovered:  {YYYY-MM-DD}
#   Incident:    {docs/incidents/filename.md}
#   Verified:    {YYYY-MM-DD}
#   Expiry:      {when to re-verify or 'stable'}

# REPLACE: Add patterns as incidents are resolved.
# Leave empty until first incident.

---

## Service Dependencies

# REPLACE: Declare what depends on what.
# The blast radius map — what breaks when X goes down.
# Example:
#
# tfxcore → tfxQDB (MySQL)
# tfxcore → tfxredis (Redis)
# tfxcore → statsdb (PostgreSQL)
# console.adswire.io → api.adswire.io (internal API)
# api.adswire.io → tenant databases (per-tenant PG)

---

## Known Edge Cases

# REPLACE: Things that behave unexpectedly and why.
# Non-obvious operational facts that agents need
# to know before acting.
# Example:
#
# - fail2ban on staging VM bans source IP after
#   MaxAuthTries exhaustion. GSSAPI burns 2 slots
#   per attempt. Wrong key in inventory + GSSAPI
#   = 4 slots burned per Ansible run.
#   Unban: fail2ban-client set sshd unbanip {ip}
#
# - Hetzner hot-swap leaves GRUB referencing old
#   disk by-id. Requires KVM to fix boot stack.
#   See Failure Patterns → Boot stack broken.

---

## Incident Index

# Auto-populated. One line per resolved incident.
# Full records in docs/incidents/
# Format: YYYY-MM-DD | node | pattern | docs/incidents/file.md

# REPLACE: Add entries as incidents are resolved.
