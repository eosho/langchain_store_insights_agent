# GitHub Issue Creator Acceptance Criteria

Validation rules for generated GitHub issues.

## Required Sections

Every generated issue MUST include:

1. **Summary** - One clear sentence describing the problem
2. **Reproduction Steps** - Numbered, clear steps to reproduce
3. **Expected Behavior** - What should happen
4. **Actual Behavior** - What actually happens
5. **Impact** - Severity with justification

## Optional Sections

Include when relevant:

- **Environment** - Product, version, region, browser/OS
- **Error Details** - Formatted in code blocks
- **Visual Evidence** - Screenshots/GIFs with alt text
- **Additional Context** - Background information

## Summary Section

### ✅ CORRECT

```markdown
## Summary
Agent deployment fails silently - no error displayed, agent disappears from list
```

```markdown
## Summary
403 PERMISSION_DENIED error when publishing to Teams channel
```

### ❌ INCORRECT

```markdown
## Summary
It doesn't work
```

```markdown
## Summary
Bug
```

## Reproduction Steps

### ✅ CORRECT

```markdown
## Reproduction Steps
1. Navigate to Azure Portal > AI Foundry
2. Click "Create new agent"
3. Configure agent with name "test-agent"
4. Click "Deploy"
5. Wait for deployment to complete
6. Check agent list
```

### ❌ INCORRECT

```markdown
## Reproduction Steps
- Try to do the thing
- It doesn't work
```

## Severity Classification

### ✅ CORRECT

```markdown
## Impact
**Critical** - Production service down, affecting all customers in West US region
```

```markdown
## Impact
**High** - Users cannot complete checkout, no workaround available
```

### ❌ INCORRECT

```markdown
## Impact
**Critical** - Button color is slightly off
```

```markdown
## Impact
This is bad.
```

## Error Formatting

### ✅ CORRECT

```markdown
## Error Details
```

Error: PERMISSION_DENIED
Code: 403
RequestId: abc-123-def-456
Timestamp: 2024-01-15T10:30:00Z

```
```

### ❌ INCORRECT

```markdown
## Error Details
Error: PERMISSION_DENIED Code: 403 RequestId: abc-123
```

## Sensitive Data Handling

### ✅ CORRECT

```markdown
## Error Details
```

User ID: [USER_ID]
API Key: [REDACTED]
Project: [PROJECT_NAME]

```
```

### ❌ INCORRECT

```markdown
## Error Details
API Key: sk-1234567890abcdef
User Email: john.doe@company.com
```

## File Naming

### ✅ CORRECT

```
issues/
├── 2024-01-15-agent-deployment-fails-silently.md
├── 2024-01-16-teams-permission-denied.md
└── 2024-01-17-api-timeout-high-load.md
```

### ❌ INCORRECT

```
issues/
├── bug.md
├── issue.md
└── problem.md
```

## Checklist

Before finalizing an issue, verify:

- [ ] Summary is one clear sentence describing the problem
- [ ] Environment section includes relevant product/service info
- [ ] Reproduction steps are numbered and clear
- [ ] Expected vs Actual behavior clearly stated
- [ ] Error details in code blocks with proper formatting
- [ ] Screenshots/GIFs referenced with descriptive alt text
- [ ] Impact includes severity (Critical/High/Medium/Low) with justification
- [ ] No sensitive data exposed (use placeholders)
- [ ] File saved with `YYYY-MM-DD-description.md` naming convention

## Anti-Patterns

| Anti-Pattern | Impact | Fix |
|--------------|--------|-----|
| Vague summary | Hard to triage | Be specific about what failed |
| Missing repro steps | Can't reproduce | Number each step clearly |
| No severity | Hard to prioritize | Add Impact section with severity |
| Exposed secrets | Security risk | Use `[PLACEHOLDER]` syntax |
| Unformatted errors | Hard to read | Use code blocks |
| Generic file names | Hard to find | Use `YYYY-MM-DD-description.md` |
