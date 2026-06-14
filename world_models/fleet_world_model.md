# fleet_world_model.md

```text
Fleet topology, service graph, trust boundaries,
deployment dependency order.

Models the WHOLE — properties no single service
world model can capture.
```

> **SECURITY NOTICE**
>
> This file contains fleet topology and inter-service architecture.
>
> If this repository is **PUBLIC**:
>
> - Add `world_models/` to `.gitignore` immediately.
>   Real service names, URLs, and dependency graphs in a
>   public repo are a security incident.

---

## Fleet Topology

```text
REPLACE: list every service in the fleet
with its role, visibility, and language.

fleet:
  your-app:
    role:       primary application
    visibility: private
    language:   REPLACE
    url:        REPLACE

  your-api:
    role:       API server
    visibility: private
    language:   REPLACE
    url:        REPLACE

  your-www:
    role:       marketing site
    visibility: public
    language:   REPLACE
    url:        REPLACE
```

---

## Service Dependency Graph

```text
REPLACE: declare what depends on what.
This is the blast radius map.
What breaks when X goes down?

your-app     → your-api (internal API)
your-console → your-api (internal API)
your-api     → tenant databases (per-tenant)
your-api     → your-cache (Redis)
your-api     → your-db (primary database)
```

---

## Data Flow

```text
REPLACE: trace how a request moves through the fleet.
End to end — from user to data store and back.

User → your-www (marketing)
     → your-app (OAuth entry point)
     → your-api (authenticated operations)
     → external service API
     → tenant database (per-tenant isolation)
```

---

## Trust Boundaries

```text
REPLACE: declare the security perimeter.
What is inside? What is outside?
What crosses the boundary and how?

Internal (trusted):
  your-app ↔ your-api (shared secret header)
  your-console ↔ your-api (shared secret header)

External (untrusted):
  Users → your-app (session auth)
  API consumers → your-api (OAuth Bearer)

Shared secret:
  REPLACE: header name and rotation policy
```

---

## Deployment Dependency Order

```text
REPLACE: the order that matters for fleet releases.
What must exist before what?

1. your-db    (must be up before any app)
2. your-cache (must be up before api)
3. your-api   (must be up before app and console)
4. your-app   (OAuth server — before console)
5. your-console (depends on app OAuth)
6. your-www   (independent, deploy anytime)
```

---

## Shared Infrastructure

```text
REPLACE: assets and services shared across the fleet.
What does every service depend on that isn't a service itself?

your-misc:
  contents:    REPLACE (shared CSS, assets, scripts)
  consumed_by: REPLACE (list of services)
```

---

## Fleet-wide Failure Patterns

```text
Patterns that cross service boundaries.
Single-service patterns live in that service's
world_models/ directory.

### Pattern: {name}
  Services affected: {list}
  Symptoms:          {what each service sees}
  Cause:             {root cause}
  Recovery:          {steps}
  Discovered:        {YYYY-MM-DD}
```

---

## Related world models

```text
Pointer graph — stitch the knowledge base.
Local:
→ world_models/vendor_world_model.md
→ world_models/staging_world_model.md

Cross-repo (private fleet repos):
→ ../your-api/world_models/api_world_model.md
→ ../your-sre/world_models/infrastructure_world_model.md
```
