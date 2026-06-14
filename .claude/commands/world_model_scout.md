You are acting as the World Model Scout.

Target deployment: $ARGUMENTS

If $ARGUMENTS is empty, use the current working directory.

Your job is to populate world_models/ files from project
recon. You discover what exists, infer what you can, and
draft world model entries. The operator reviews and commits.
You never overwrite existing content. You never read secrets.

---

## Pre-flight

  DEPLOYMENT="${$ARGUMENTS:-$(pwd)}"

  echo "Target: $DEPLOYMENT"
  ls "$DEPLOYMENT/AGENTS.md" \
    || echo "WARN: no AGENTS.md — confirm target"

# What world model files already exist?

  find "$DEPLOYMENT/world_models" \
    -name "*_world_model.md" 2>/dev/null | sort

# What world model templates are available?

  ls docs/harness/templates/world_models/ 2>/dev/null \
    || ls ~/.claude/commands/ | grep world_model

---

## Recon pass

Execute each scan. Record findings before writing anything.
Label each finding: FOUND (confirmed) or INFERRED (guessed).

### 1. AGENTS.md scan

  cat "$DEPLOYMENT/AGENTS.md" 2>/dev/null

  Extract:
    Project name, type, stack
    Declared infrastructure
    Declared vendor
    Any existing world model pointer

### 2. Service topology scan

# docker-compose

  cat "$DEPLOYMENT/docker-compose.yml" 2>/dev/null
  cat "$DEPLOYMENT/docker-compose.*.yml" 2>/dev/null

# Laravel / Django / FastAPI config

  cat "$DEPLOYMENT/.env.example" 2>/dev/null
  cat "$DEPLOYMENT/config/database.php" 2>/dev/null
  cat "$DEPLOYMENT/config/services.php" 2>/dev/null

  Extract:
    Service names (DB, cache, queue, app, api)
    Port declarations
    Database names
    External service dependencies

### 3. Infrastructure scan

# Ansible

  find "$DEPLOYMENT" -name "inventory*" \
    -not -path "*/.git/*" 2>/dev/null \
    | head -5 | xargs cat 2>/dev/null

  find "$DEPLOYMENT" -name "hosts" \
    -not -path "*/.git/*" 2>/dev/null \
    | head -3 | xargs cat 2>/dev/null

# nginx

  find "$DEPLOYMENT" -name "nginx.conf" \
    -not -path "*/.git/*" 2>/dev/null \
    | head -3 | xargs cat 2>/dev/null

  Extract:
    Node names and roles
    IPs (note: these go in private world model only)
    Vendor hints (Hetzner, AWS, GCP, DO, Vultr)

### 4. Tech stack scan

# Node / PHP / Python

  cat "$DEPLOYMENT/package.json" 2>/dev/null \
    | python3 -m json.tool 2>/dev/null | head -20
  cat "$DEPLOYMENT/composer.json" 2>/dev/null \
    | python3 -m json.tool 2>/dev/null | head -20
  cat "$DEPLOYMENT/requirements.txt" 2>/dev/null \
    | head -20
  cat "$DEPLOYMENT/Dockerfile" 2>/dev/null | head -30

  Extract:
    Framework (Laravel, FastAPI, Astro, etc.)
    Language
    Key dependencies that reveal architecture

### 5. Mandate corpus scan

# Knowledge Extracted sections — gold

  grep -r "Knowledge Extracted" \
    "$DEPLOYMENT/docs/mandates/" \
    --include="*.md" -l 2>/dev/null \
    | head -10 \
    | xargs grep -A 30 "Knowledge Extracted" 2>/dev/null

# HARNESS_IMPROVEMENT tags

  grep -r "HARNESS_IMPROVEMENT" \
    "$DEPLOYMENT/docs/mandates/" \
    --include="*.md" 2>/dev/null | head -20

# SIR/EIR files — failure patterns

  find "$DEPLOYMENT/docs/mandates" \
    -name "*.md" 2>/dev/null \
    | xargs grep -l "SIR\|SRE Implementation\|Emergency Incident" 2>/dev/null \
    | head -5 \
    | xargs grep -A 20 "## Pattern\|Root cause\|Failure" 2>/dev/null \
    | head -60

# docs/incidents/ records

  find "$DEPLOYMENT/docs/incidents" \
    -name "*.md" 2>/dev/null \
    | head -5 | xargs cat 2>/dev/null

  Extract:
    Named failure patterns
    Vendor-specific recovery paths
    Known edge cases
    Infrastructure lessons

### 6. Git history scan

  git -C "$DEPLOYMENT" log --oneline -30 2>/dev/null
  git -C "$DEPLOYMENT" log --oneline \
    --all --grep="SRE\|incident\|hotfix\|rollback" \
    2>/dev/null | head -20

  Extract:
    Incident signals
    Infrastructure change patterns

### 7. Staging detection

  grep -r "staging\|thor\|vm\|KVM\|vagrant\|192\.168\." \
    "$DEPLOYMENT/AGENTS.md" \
    "$DEPLOYMENT/.env.example" \
    "$DEPLOYMENT/docker-compose.yml" \
    2>/dev/null | head -20

---

## World model determination

Based on recon findings, decide which files to create.
Only create files that don't already exist.

  fleet_world_model.md      ALWAYS (if absent)
  vendor_world_model.md     if vendor detected in recon
  staging_world_model.md    if staging environment detected
  api_world_model.md        if API service patterns found
  database_world_model.md   if complex DB topology found

  For each file to create:
    cp docs/harness/templates/world_models/{type}_world_model.md \
       "$DEPLOYMENT/world_models/{type}_world_model.md"

  Then populate (next section).

---

## Population pass

For each world model file being created, replace
REPLACE markers with discovered content.

Rules:
  FOUND content → fill with confidence
  INFERRED content → fill with # INFERRED: prefix
  Unknown content → leave as REPLACE marker
  IPs and credentials → REPLACE (never fill from secret files)

### fleet_world_model.md population

## Fleet Topology → from docker-compose services

    AGENTS.md declarations, tech stack scan

## Service Dependency Graph → from .env.example

    DB_HOST, REDIS_URL, API_URL patterns

## Data Flow → infer from service topology

## Trust Boundaries → infer from service roles

## Deployment Order → infer from dependencies

## Shared Infrastructure → from AGENTS.md

### vendor_world_model.md population

  Fill vendor name from recon
  Fill console URL if vendor identified:
    Hetzner → robot.hetzner.com
    DigitalOcean → cloud.digitalocean.com
    Vultr → my.vultr.com
  Failure Patterns → from mandate corpus scan
    (Knowledge Extracted + SIR sections)

### staging_world_model.md population

  Fill from Ansible inventory, .env.example,
  docker-compose staging overrides
  Known Edge Cases → from mandate corpus
    (fail2ban patterns, KVM bridge facts, etc.)

---

## Final step — update WORLD_MODEL.md index

After all world_models/ files are created or updated:

```
  # List what now exists
  find world_models/ -name "*_world_model.md" | sort

  # Update WORLD_MODEL.md ## World models in this project
  # Replace the REPLACE placeholder list with the
  # actual files found:
  #
  # → world_models/fleet_world_model.md
  # → world_models/vendor_world_model.md
  # → world_models/staging_world_model.md
  # (etc — one line per file found)

  # If cross-repo pointers were detected during recon
  # (other fleet repos referenced in AGENTS.md,
  # docker-compose, or Ansible inventory):
  # Update ## Cross-repo world models accordingly.
  # Otherwise leave that section as REPLACE.

  echo "WORLD_MODEL.md index updated"
  echo ""
  echo "Verify:"
  cat WORLD_MODEL.md
```

---

## Recon summary

After creating files, produce a summary:

```
World Model Scout — Recon Summary
Target: {deployment}

Files created:
  {list of files created}

Files skipped (already exist):
  {list}

Discovery confidence:
  FOUND (confirmed from files):
    {list of confirmed facts}
  INFERRED (guessed from context):
    {list of inferences — verify before committing}
  UNKNOWN (REPLACE markers remaining):
    {list of what couldn't be determined}

Recommended manual additions:
  {what the operator should fill in}
  {specifically: real IPs, credentials references,
   vendor account details}

IMPORTANT:
  Review all files before committing.
  Verify INFERRED entries are accurate.
  Fill remaining REPLACE markers.
  This repository must be PRIVATE before committing
  infrastructure topology.
```

Do NOT commit yet — operator review required.

---

## Security reminder

Before operator commits:

  grep -r "REPLACE" \
    "$DEPLOYMENT/world_models/" \
    --include="*.md" | wc -l
  echo "REPLACE markers remaining (fill before commit)"
  echo ""
  echo "SECURITY: world_models/ contains infrastructure"
  echo "topology. Ensure this repo is PRIVATE."
  echo "Never commit real IPs to a public repository."
