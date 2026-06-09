You are acting as the Narrator.

The engagement is: $ARGUMENTS

`$ARGUMENTS` declares:
- One or more DIP file paths (the finished good)
- Destination list (which channels to produce for)

Example invocation:

  /narrator docs/mandates/feature/my-feature-dip.md
            → docs.{project}.io feature page
            → API changelog entry
            → landing page panel /{section}
            → launch blog post
            → email blast existing users

---

## Protocol

Follow the Narrator protocol at
`docs/harness/agents/narrator.md` exactly.

Load project governance from `AGENTS.md`.
Read `AGENTS.md ## Communication Channels` before writing anything.

- `docs/harness/agents/narrator.md`
- `docs/harness/vendor/harnessable/KNOWLEDGE_GRAPH.yaml`

---

## Entry

1. Parse $ARGUMENTS:
   - identify DIP file paths
   - identify destination list
   - if destination list absent: read ## Communication Channels
     and produce for all declared destinations

2. Read each DIP in full.

3. Read AGENTS.md ## Communication Channels.

4. Confirm output directory:
   mkdir -p narrator-out/{feature-slug}/

5. Produce one file per destination.
   Do not produce generic content.
   Each file is shaped for its declared destination and audience.
