---
name: speckit-git-commit
description: Auto-commit changes after a Spec Kit command completes
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: github-spec-kit
  source: git:commands/speckit.git.commit.md
---

# Auto-Commit Changes

Automatically stage and commit all changes after a Spec Kit command completes, following strict Git Flow conventions and mandatory commit guidelines.

## Mandatory Guidelines

### Feature Branch Naming
- All new branches **MUST** follow the pattern: `feature/T<id>-<description>`
- Example: `feature/T102-graphql-schema-updates`
- Violation of this pattern will cause the commit to fail

### Commit Message Requirements
- **NO** `Co-Authored-By:` footers - commits are authored solely by the project author
- **NO** Claude model attribution or credits in commit messages
- Commit messages must be descriptive and reference task/feature IDs when applicable
- Format: `[SCOPE] (OPTIONAL-ID): Brief description` or task-specific conventions

### Pull Request & Merging
- All feature branches must go through Pull Request review before merging to main
- PRs must reference the related task/issue
- Squash commits on merge to maintain clean history
- Delete feature branch after successful merge

## Behavior

This command is invoked as a hook after (or before) core commands. It:

1. **Validates** current branch name matches `feature/T<id>-*` pattern (if not main/master)
2. Determines the event name from the hook context (e.g., if invoked as an `after_specify` hook, the event is `after_specify`; if `before_plan`, the event is `before_plan`)
3. Checks `.specify/extensions/git/git-config.yml` for the `auto_commit` section
4. Looks up the specific event key to see if auto-commit is enabled
5. Falls back to `auto_commit.default` if no event-specific key exists
6. Uses the per-command `message` if configured, otherwise a default message
7. **Sanitizes** commit message to remove any Claude attribution or co-author footers
8. If enabled and there are uncommitted changes, runs `git add .` + `git commit`

## Execution

Determine the event name from the hook that triggered this command, then run the script:

- **Bash**: `.specify/extensions/git/scripts/bash/auto-commit.sh <event_name>`
- **PowerShell**: `.specify/extensions/git/scripts/powershell/auto-commit.ps1 <event_name>`

Replace `<event_name>` with the actual hook event (e.g., `after_specify`, `before_plan`, `after_implement`).

**Important**: The script will validate branch naming and sanitize commit messages before committing.

## Git Flow Methodology

This project enforces the Git Flow branching model:

### Branch Types
- **master/main**: Production-ready code, all merges from release branches
- **feature/T<id>-\***: Feature development branches (created from develop)
  - Must follow naming convention: `feature/T<id>-description`
  - Example: `feature/T102-add-graphql-mutations`
- **develop**: Integration branch for features (optional, depends on project config)
- **release/\***: Release preparation branches
- **hotfix/\***: Emergency production fixes

### Workflow
1. Create feature branch: `git checkout -b feature/T<id>-description`
2. Develop and commit changes (following mandatory guidelines above)
3. Push to remote: `git push -u origin feature/T<id>-description`
4. Create Pull Request for code review
5. After approval, merge to develop/main with squash commits
6. Delete feature branch after merge

## Configuration

In `.specify/extensions/git/git-config.yml`:

```yaml
auto_commit:
  default: false          # Global toggle — set true to enable for all commands
  after_specify:
    enabled: true          # Override per-command
    message: "spec: Add specification for feature"
    disable_claude_comments: true
  after_plan:
    enabled: false
    message: "plan: Add implementation plan"
    disable_claude_comments: true
  after_implement:
    enabled: true
    message: "feat: Implement feature changes"
    disable_claude_comments: true
```

### Message Guidelines
- Use conventional commit format when possible: `type(scope): description`
- Common types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `spec`, `plan`
- **NEVER** include `Co-Authored-By:` footers
- **NEVER** add Claude, AI assistant, or model attribution
- Keep messages clear, concise, and focused on the change

## Validation & Error Handling

### Pre-Commit Validation
- **Branch Naming**: Validates branch name matches `feature/T<id>-*` pattern (exempts main/master)
  - If invalid on feature branch: **FAILS** with error message, requires branch rename
- **Commit Message Sanitization**: Automatically removes any:
  - `Co-Authored-By:` footers
  - Claude, AI assistant, or model attribution lines
  - Automated tool comments marked for removal

### Graceful Degradation
- If Git is not available or the current directory is not a repository: skips with a warning
- If no config file exists: skips (disabled by default)
- If no changes to commit: skips with a message
- If branch naming validation fails: **ABORTS commit** with clear error and guidance
- If Claude comments are detected: removes them and warns user in log