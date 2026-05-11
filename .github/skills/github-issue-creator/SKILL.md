---
name: github-issue-creator
description: "Transform raw notes, error logs, voice dictation, or screenshots into structured GitHub issues. Use when user pastes bug info, error messages, or informal descriptions and wants a clean, actionable issue report."
argument-hint: 'Paste the error, bug notes, or screenshot'
---

# GitHub Issue Creator

Convert messy input into clean, actionable GitHub issues with proper structure.

## When to Use This Skill

- User pastes error logs or stack traces
- User dictates bug descriptions informally
- User wants to convert notes into a GitHub issue
- User has screenshots/GIFs to document a bug
- User needs help structuring a bug report or feature request

## Prerequisites

```bash
# Install GitHub CLI (if not present)
# macOS: brew install gh
# Linux: see https://github.com/cli/cli/blob/trunk/docs/install_linux.md
# Windows: winget install --id GitHub.cli

# Authenticate
gh auth login
gh auth status
```

## Issue Template

```markdown
## Summary
[One-line description of the issue]

## Environment
- **Product/Service**: [Name]
- **Region/Version**: [Version or region]
- **Browser/OS**: [If relevant]

## Reproduction Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Error Details
```
[Error message/code if applicable]
```

## Visual Evidence
[Reference to attached screenshots/GIFs]

## Impact
[Severity: Critical/High/Medium/Low + brief explanation]

## Additional Context
[Any other relevant details]
```

## Severity Guidelines

| Severity | Definition | Examples |
|----------|------------|----------|
| **Critical** | Service down, data loss, security issue | Production outage, auth bypass |
| **High** | Major feature broken, no workaround | Cannot deploy, checkout fails |
| **Medium** | Feature impaired, workaround exists | Slow performance, alternative available |
| **Low** | Minor inconvenience, cosmetic | Typo, UI alignment |

## Guidelines

**Be crisp**: Every word should add value. No fluff.

**Extract structure from chaos**: Voice dictation and raw notes contain facts buried in casual language. Pull them out.

**Infer missing context**: If user mentions "same project" or "the dashboard", use conversation context to fill in specifics.

**Placeholder sensitive data**: Use `[PROJECT_NAME]`, `[USER_ID]`, `[REDACTED]` for anything sensitive.

**Match severity to impact**: Critical ≠ "I'm frustrated". Critical = "service is down".

**Image handling**: Reference attachments inline with descriptive alt text:
```markdown
![Error dialog showing 403 permission denied](error-screenshot.png)
```

## Output Location

Create issues as markdown files in `/issues/` directory at repo root.

**Naming convention**: `YYYY-MM-DD-short-description.md`

```
issues/
├── 2024-01-15-agent-deployment-fails-silently.md
├── 2024-01-16-teams-permission-denied.md
└── 2024-01-17-api-timeout-high-load.md
```

## Examples

### Voice Dictation → Issue

**Input:**
> so I was trying to deploy the agent and it just failed silently no error nothing the workflow ran but then poof gone from the list had to refresh and try again three times

**Output:**
```markdown
## Summary
Agent deployment fails silently - no error displayed, agent disappears from list

## Environment
- **Product/Service**: Azure AI Foundry
- **Region/Version**: [REGION]

## Reproduction Steps
1. Navigate to agent deployment
2. Configure and deploy agent
3. Observe workflow completes
4. Check agent list

## Expected Behavior
Agent appears in list with deployment status, errors shown if deployment fails

## Actual Behavior
Agent disappears from list. No error message. Requires page refresh and retry.

## Impact
**High** - Blocks agent deployment workflow, no feedback on failure cause

## Additional Context
Required 3 retry attempts before successful deployment
```

### Error Paste → Issue

**Input:**
> Error: PERMISSION_DENIED when publishing to Teams channel. Code: 403. Was working yesterday.

**Output:**
```markdown
## Summary
403 PERMISSION_DENIED error when publishing to Teams channel

## Environment
- **Product/Service**: Copilot Studio → Teams integration
- **Region/Version**: [REGION]

## Reproduction Steps
1. Configure agent for Teams channel
2. Attempt to publish

## Expected Behavior
Agent publishes successfully to Teams channel

## Actual Behavior
Returns `PERMISSION_DENIED` with code 403

## Error Details
```
Error: PERMISSION_DENIED
Code: 403
```

## Impact
**High** - Blocks Teams integration, regression from previous working state

## Additional Context
Was working yesterday - possible permission/config change or service regression
```

## Creating Issues with GitHub CLI

After generating the markdown, create the issue:

```bash
# Create issue from file
gh issue create --title "Agent deployment fails silently" --body-file issues/2024-01-15-agent-deployment-fails-silently.md

# With labels
gh issue create --title "403 error on Teams publish" --body-file issues/2024-01-16-teams-permission-denied.md --label "bug,priority:high"

# Assign to someone
gh issue create --title "API timeout under load" --body-file issues/2024-01-17-api-timeout-high-load.md --assignee "@me"
```

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Vague summary ("It doesn't work") | Specific description of what failed |
| Missing repro steps | Numbered, clear steps |
| No severity | Impact section with justification |
| Exposed secrets | Use `[PLACEHOLDER]` syntax |
| Unformatted errors | Code blocks with proper formatting |
| Generic filenames (`bug.md`) | `YYYY-MM-DD-description.md` |

## References

- [Acceptance Criteria](references/acceptance-criteria.md) — Validation rules with correct/incorrect examples
- [GitHub Issue Best Practices](https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-an-issue)
- [GitHub CLI Issue Commands](https://cli.github.com/manual/gh_issue_create)
