# packages/hallmark/

Harnessable adapter for Hallmark — anti-AI-slop
design skill by Nutlope / Together AI.

## What this adapter provides

  skills/hallmark.md         /hallmark command
  skills/hallmark_study.md   /hallmark-study command
  adapter/designer_ext.md    Designer role extension
  adapter/rubric.md          65-gate slop Rubric
  adapter/design_world_model.md  design domain world model

## What this adapter does NOT provide

The Hallmark package itself. The adapter is a
governance bridge — not the package.

## Installation (required before use)

  npx skills add nutlope/hallmark

Verify:
  ls ~/.agents/skills/hallmark/SKILL.md

If this file does not exist, /hallmark and
/hallmark-study will not function.

## Verification

  ls ~/.agents/skills/hallmark/SKILL.md \
    && echo "Hallmark: installed" \
    || echo "Hallmark: NOT installed — run:
             npx skills add nutlope/hallmark"
