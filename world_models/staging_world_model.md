# staging_world_model.md

```text
Staging environment topology, known issues,
non-obvious infrastructure facts.
Separate from production — staging has its own
failure patterns and edge cases.
```

> **SECURITY NOTICE**
>
> Keep this file in a **PRIVATE** repository.
> Staging IPs and topology reveal production
> architecture patterns.

---

## Staging Topology

```text
REPLACE: staging infrastructure

nodes:
  your-staging-vm:
    host:    REPLACE (KVM host or cloud instance)
    ip:      REPLACE — private repo only
    os:      REPLACE
    purpose: staging application stack

network:
  bridge:    REPLACE (e.g. KVM bridge gateway)
             note: fail2ban bans the BRIDGE IP,
             not the VM IP — affects all VMs
             behind the same bridge
```

---

## Known Edge Cases

```text
REPLACE: staging-specific behaviours that differ
from production. Non-obvious facts agents need
before acting on staging.

Example (generic — replace with real):
- fail2ban bans the KVM bridge gateway, not the
  VM IP. One ban blocks all staging VMs.
  Unban: fail2ban-client set sshd unbanip {bridge-ip}

- GSSAPI burns 2 of 6 MaxAuthTries per attempt.
  Always disable: GSSAPIAuthentication=no

- Staging uses different SSH keys than production.
  Verify ansible_ssh_private_key_file before running.
```

---

## Failure Patterns

```text
### Pattern: {short name}
  Layer:      {layer}
  Symptoms:   {observable}
  Cause:      {root cause}
  Diagnosis:  {how to confirm}
  Procedure:
    1. {step}
  Discovered: {YYYY-MM-DD}
```

---

## Related world models

```text
→ world_models/fleet_world_model.md
→ world_models/vendor_world_model.md
```
