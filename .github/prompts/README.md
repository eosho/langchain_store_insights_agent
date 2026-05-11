# Copilot Chat Slash Commands

Custom slash commands for GitHub Copilot Chat to automate common development workflows.

## Available Commands

### Agent Commands

| Command     | Purpose                                                                        | Usage       |
| ----------- | ------------------------------------------------------------------------------ | ----------- |
| `/builder`  | Build anything end-to-end: features, tests, infrastructure, bug fixes          | `/builder`  |
| `/planner`  | Plan anything: requirements, design docs, ADRs, task decomposition             | `/planner`  |
| `/reviewer` | Review anything: code quality, security, architecture compliance               | `/reviewer` |

### Workflow Commands

| Command              | Purpose                                           | Routes To   |
| -------------------- | ------------------------------------------------- | ----------- |
| `/new-feature`       | Gather requirements, then implement end-to-end    | @Builder    |
| `/fix-bug`           | Diagnose with repro steps, fix with tests         | @Builder    |
| `/code-review`       | Comprehensive quality + security review           | @Reviewer   |
| `/design-api`        | Design REST endpoints, schemas, contracts         | @Planner    |
| `/devsetup`          | Execute development environment setup             | —           |
| `/init-local`        | Scaffold new project from local repo              | —           |
| `/upgrade-deps`      | Check for pyproject.toml dependency updates       | —           |
| `/build-foundry-agent` | Build AI agent with Microsoft Agent Framework   | @Builder    |
| `/build-multi-agent` | Build multi-agent workflows with handoffs         | @Builder    |

### Test Commands

Self-validating prompts to verify agents/skills work correctly. See [tests/README.md](tests/README.md).

| Command                | Purpose                                           | Validates   |
| ---------------------- | ------------------------------------------------- | ----------- |
| `/test-agent-framework`| Test agent-framework-py skill                     | AzureAIAgentsProvider, FunctionTool patterns |
| `/test-fastapi-crud`   | Test fastapi-py skill                             | CRUD endpoints, Pydantic schemas |
| `/test-azure-security` | Test azure-security skill                         | Security-first IaC patterns |
| `/test-cloud-architect`| Test cloud-solution-architect skill               | ADR format, WAF review |
| `/test-builder-e2e`    | Test @Builder agent end-to-end                    | Full implementation cycle |

## Creating New Commands

1. Create `.prompt.md` file in this directory
2. Add YAML frontmatter:

   ```yaml
   ---
   agent: agent
   name: command-name
   description: Brief description
   tools: []
   ---
   ```

3. Write instructions in markdown
4. Use in Copilot Chat as `/command-name`

See [GitHub Copilot Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) for details.
