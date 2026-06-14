# vendor_world_model.md

```text
Vendor capabilities, recovery tools,
non-obvious behaviours, support paths.
One entry per vendor this project depends on.
```

> **SECURITY NOTICE**
>
> Keep this file in a **PRIVATE** repository.
> Vendor account details and recovery URLs reveal
> infrastructure topology.

---

## your-hosting-vendor

```text
REPLACE: your infrastructure hosting provider

console:      REPLACE (vendor management URL)
rescue_mode:  REPLACE (how to access KVM/rescue)
support:      REPLACE (support URL or contact)

Non-obvious behaviours agents must know:
  REPLACE: e.g. "hot-swap leaves boot stack broken"
  REPLACE: e.g. "KVM required to diagnose below OS layer"

Recovery tools:
  REPLACE: e.g. virtual KVM, rescue mode, IPMI
```

---

## your-dns-vendor

```text
REPLACE: DNS and CDN provider

console:            REPLACE
propagation_window: REPLACE (typical TTL)
cache_purge:        REPLACE (how to purge CDN cache)
proxy_mode:         REPLACE (orange/grey cloud behaviour)
```

---

## your-payment-vendor

```text
REPLACE: payment processing provider

dashboard:    REPLACE
webhook_test: REPLACE (how to test webhooks locally)
note:
  REPLACE: non-obvious webhook behaviours
```

---

## Failure Patterns

```text
### Pattern: {vendor} — {short name}

  Vendor:     {vendor}
  Layer:      {Hardware | Network | Service | Auth}
  Symptoms:   {what agents observe}
  Cause:      {what actually happened}
  Tool:       {what accesses the right layer}
  Procedure:
    1. {step}
  Discovered: {YYYY-MM-DD}
  Verified:   {YYYY-MM-DD}
```

---

## Related world models

```text
→ world_models/fleet_world_model.md
→ world_models/staging_world_model.md
```
