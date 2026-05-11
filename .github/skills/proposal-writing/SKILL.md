---
name: proposal-writing
description: 'Write design proposals, RFCs, and architecture decision records. Use when: user asks to "write a proposal", "create a design doc", "RFC for feature", or needs team buy-in for a change.'
argument-hint: 'Describe the feature or change you want to propose'
---

# Proposal Writing

Create clear, actionable technical proposals that drive decisions.

## When to Use

- "write a proposal" / "create a design doc"
- "RFC for [feature]"
- Feature needs team buy-in or cross-team coordination
- Architecture decision needed

**Skip this skill for:** Simple bug fixes, minor changes, obvious implementations.

## Procedure

### 1. Find Proposals Location

<!-- Check for existing proposals folder in the workspace -->

Check for existing proposals folder:
- `docs/proposals/` (most common)
- `proposals/`, `docs/design/`, `docs/rfcs/`

**If none exists:** Create `docs/proposals/`

### 2. Create Proposal File

<!-- Copy template and fill in all sections based on user's input -->

1. Copy [template](../../../docs/proposals/template.md)
2. Name it descriptively: `feature-name.md` (not `proposal-1.md`)
3. Fill in all sections based on user's input

### 3. Create Tracking Issue (Optional)

<!-- Only if user requests it -->

If requested, create a GitHub issue or backlog task linking to the proposal.

### 4. Update Index (If Exists)

<!-- Add entry to proposals table if README.md exists -->

If `docs/proposals/README.md` has a proposals table, add an entry.

## Resources

- [Template](../../../docs/proposals/template.md) - Copy this to start
- [Writing Guidelines](./references/guidelines.md) - Good/bad examples, anti-patterns
