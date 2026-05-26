# Knowledge Graph

The `KNOWLEDGE_GRAPH.yaml` at the repository root is the authoritative semantic
layer of the Harnessable framework. It defines every concept in the `harnessable`
namespace — roles, artifacts, enumerations, events, and their relationships — as a
machine-readable, queryable graph.

This document explains the model, why it exists, and how to extend it in a project.

---

## Why a knowledge graph and not a glossary

A glossary defines terms in isolation. A knowledge graph declares relationships
between concepts — types, hierarchies, ownership, constraints, and what each
concept produces, consumes, requires, and prohibits.

That difference matters in two situations that arise constantly in production work:

**Cross-domain terminology collisions.** Two platforms may use the same word with
different meanings — deliberately. A flat glossary cannot express that
`google_ads.Campaign` and `meta.Campaign` are distinct concepts that share a label.
A graph holds both, links them with an explicit alignment relationship, and annotates
the divergence so any agent or guard operating across both platforms knows not to
treat them as interchangeable.

**Unfamiliar domains.** When operating in a system you did not build and do not yet
fully understand, domain intuition is absent. The knowledge graph is the written-down
substitute for that intuition — a structured record of what each concept means, what
it relates to, and where the dangerous assumptions live.

---

## What belongs in the framework graph

`KNOWLEDGE_GRAPH.yaml` contains only the `harnessable` namespace. Framework concepts
only. It does not know about Google Ads, Shopify, MySQL, or any domain specific to
any project.

If you find yourself wanting to add a domain concept to `KNOWLEDGE_GRAPH.yaml`,
that is a signal to extend it in a project-level graph instead.

---

## Vendoring the framework graph

Harnessable is a dependency, not a directory you modify. When you install it into a
project, copy the framework files and pin the version you copied.

Recommended project layout after `cp -r framework/ docs/harness/`:

```text
your-project/
  docs/
    harness/
      agents/                     ← Tier 1: copy and own
      hooks/                      ← Tier 1: copy and own
      templates/                  ← Tier 1: copy and own
      vendor/
        harnessable/
          KNOWLEDGE_GRAPH.yaml    ← Tier 2: vendored, never modified
          HARNESSABLE_VERSION     ← one line: the release tag or commit SHA
          references/             ← Tier 2: vendored, never modified
    knowledge-graph.yaml          ← project-owned, extends the vendored copy
```

`HARNESSABLE_VERSION` content:

```text
v0.2.1
```

To update: replace `docs/harness/vendor/harnessable/` with the new release,
update `HARNESSABLE_VERSION`, and review the changelog for changes to the
`harnessable` namespace that may affect concepts your project graph depends on.
Never edit files inside `docs/harness/vendor/harnessable/`.

---

## Writing a project-level knowledge graph

A project knowledge graph lives at `docs/knowledge-graph.yaml`. It declares the
project's domain namespaces and their concepts, and extends the vendored framework
graph.

Minimal structure:

```yaml
meta:
  version: "0.1.0"
  layer: project
  extends: docs/harness/vendor/harnessable/KNOWLEDGE_GRAPH.yaml
  harnessable_version: "v0.2.1"   # must match HARNESSABLE_VERSION
  project: your-project-name

namespaces:
  your_domain:
    description: Concepts specific to this project's domain.
    source: internal
  external_platform:
    description: Concepts from an external platform or API.
    source: https://docs.example-platform.com
```

All `harnessable.*` concepts are available via the `extends` reference. You do not
redefine them. You reference them.

---

## Declaring domain concepts

Each concept is keyed by `namespace.ConceptName`. Use the same relationship fields
the framework graph uses for consistency — agents loading both files see a uniform
structure.

```yaml
concepts:

  your_domain.Campaign:
    type: concept
    definition: >
      Your precise definition for this project. Do not import platform
      documentation verbatim — write what this concept means in the
      context of this system and how it behaves here.
    properties:
      budget_owner: true
    contains: [your_domain.AdGroup]

  your_domain.AdGroup:
    type: concept
    definition: >
      Mid-tier container under a Campaign. Groups ads by shared targeting.
    parent: your_domain.Campaign
    contains: [your_domain.Ad]
```

---

## Handling terminology collisions across platforms

When two namespaces use the same label for concepts that differ in meaning,
declare the collision explicitly in an `alignments` section. Do not silently
treat them as equivalent.

```yaml
alignments:

  - id: campaign_label_collision
    concepts: [platform_a.Campaign, platform_b.Campaign]
    relationship: collides_with
    shared_label: Campaign
    divergence: >
      Both platforms use "Campaign" as the top-level unit, but ownership
      of budget and bid strategy differs. Treat as distinct concepts
      despite identical labels.
    safe_assumption: false

  - id: adgroup_adset_functional_equivalence
    concepts: [platform_a.AdGroup, platform_b.AdSet]
    relationship: similar_to
    divergence: >
      Functionally similar mid-tier containers, but differ in what
      properties each owns. Do not assume interchangeability.
    safe_assumption: false

  - id: quality_score_no_equivalent
    concepts: [platform_a.QualityScore]
    relationship: has_no_equivalent_in
    namespaces: [platform_b]
    note: >
      Platform A-only concept. Do not attempt to map or infer an
      equivalent when operating across both platforms.
```

Valid `relationship` values and what they assert:

| Value | Meaning |
|---|---|
| `same_as` | Concepts are semantically identical across namespaces. Safe to treat as equivalent. |
| `similar_to` | Functionally related but not identical. Understand the divergence before assuming equivalence. |
| `collides_with` | Same label, different meaning. Never treat as equivalent. |
| `has_no_equivalent_in` | Concept exists in one namespace with no counterpart in another. |

---

## Loading the graph in an agent session

At the start of each agent session, tell the agent to load both the framework
graph and the project graph:

```
Load and reason against both knowledge graphs before taking any action
involving domain concepts:

Framework graph: docs/harness/vendor/harnessable/KNOWLEDGE_GRAPH.yaml
Project graph:   docs/knowledge-graph.yaml

When a concept appears in both, the project graph definition governs.
When a cross-namespace alignment is marked safe_assumption: false, treat
the concepts as distinct regardless of shared labels.
```

---

## The Knowledge Graph as Pipeline Output

Every role is a knowledge scout. The pipeline produces two parallel outputs:
working software and an enriched knowledge graph. Recon discoveries,
implementation findings, and QA observations all generate knowledge — about
the domain, about platform terminology, about where concepts collide. That
knowledge belongs in the graph, not only in DIP and TIR documents where it
is findable but not queryable.

The `harnessable.DiscoveryClass.ONTOLOGY_GAP` discovery class is the mechanism.
Any role that encounters an undeclared concept halts, files the gap, and resumes
only after the graph is amended. The pipeline gates at PLANNED and DONE enforce
this: the graph must be enriched as a condition of progression, not as a
post-mandate cleanup task.

The Architect carries the obligation at both ends. At mandate open, every
concept in the DMT must be grounded in the project graph — undefined intent is
a blocker on mandate creation. At mandate close, the graph must reflect
everything the mandate surfaced — unresolved gaps block DONE.

---

## Graph relationship reference

These relationship keys are used consistently across both the framework graph
and project graphs. Agents and guards interpret them uniformly.

| Key | Meaning |
|---|---|
| `type` | The concept's base type or parent class. |
| `definition` | Precise meaning in this namespace. Not a copy of external documentation. |
| `subclasses` | Concepts that inherit from this one. |
| `produced_by` | The Role responsible for creating this Artifact. |
| `consumed_by` | The Role that reads and acts on this Artifact. |
| `requires` | Artifact that must exist before this one can be produced. |
| `required_before` | Artifact that cannot be produced until this one is complete. |
| `embedded_in` | This Artifact lives inside another rather than as a standalone file. |
| `contains` | Concepts or Artifacts nested within this one. |
| `triggers_status` | Board status set when this concept is produced or a value is applied. |
| `prohibited_from` | Actions this Role must never perform. |
| `constraints` | Invariants that must hold. Violation is a protocol error. |
| `properties` | Named attributes with values relevant to guards or agent reasoning. |
| `safe_assumption` | Used in alignments. `false` means agents must not assume equivalence. |
| `halts_work` | Used in DiscoveryClass values. Whether filing this class stops execution. |
