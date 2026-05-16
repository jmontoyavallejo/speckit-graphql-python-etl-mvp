---
description: "Improve speckit-implement workflow with automated pre-flight checks"
---

# Feature Specification: Improve Speckit Implement Workflow

**Goal**: Establish and automate a pre-flight validation workflow that ensures `/speckit-implement` performs consistent repository state checks before initiating implementation tasks.

---

## User Problem

When running `/speckit-implement`, there's no automated verification that:
- The repository is in a consistent state across branches
- `develop` branch is most ahead of all other branches
- Stale feature branches are merged or cleaned up  
- Task completion status is properly tracked before starting new work
- New feature branches follow the gitflow naming convention

This leads to accidental out-of-sync branches, missed merges, and unclear which tasks are pending.

---

## Requirements

### R1: Pre-Flight Branch Status Check
When `/speckit-implement` is invoked, it must:
1. Verify the current branch is a valid feature branch (`feature/T<id>-<name>`)
2. Abort with clear error if on `master` or `develop` directly
3. Show current branch name and status

**Acceptance Criteria**:
- Script checks `git rev-parse --abbrev-ref HEAD`
- Validates against pattern `feature/T[0-9]+.*`
- Error message clearly states: "Must be on a feature branch"

### R2: Develop Branch Ahead Verification
Verify that `develop` branch is the most ahead of all feature branches:
1. Fetch latest from remote
2. Compare commit counts: `git rev-list --count <branch>..develop`
3. If any branch is ahead of `develop`, prompt user to merge or rebase

**Acceptance Criteria**:
- Script compares all local/remote branches to `develop`
- Shows commit count diff for each branch
- Prompts: "Branch X is ahead of develop by Y commits. Merge now? (yes/no)"

### R3: Auto-Merge Stale Feature Branches (Optional)
If a feature branch is fully merged into another branch, offer to delete it.

**Acceptance Criteria**:
- Detect merged branches: `git branch --merged develop`
- Offer: "Branch X is merged. Delete? (yes/no)"
- Clean up with `git branch -d <branch>`

### R4: Task Completion Inventory
Before allowing implementation to proceed:
1. Check `tasks.md` in the feature directory
2. Count total tasks: `- [X]` vs `- [ ]`
3. Report: "## Task Status: 103/103 completed (1 pending)"

**Acceptance Criteria**:
- Parse tasks.md for checkbox syntax
- Display summary: `Completed: 103 | Pending: 0`
- If pending tasks exist, ask: "Proceed with remaining tasks? (yes/no)"

### R5: New Feature Branch Creation (If All Tasks Done)
If all tasks in current feature are complete and user confirms, create a new feature branch:
1. Prompt for next task ID (suggest highest+1)
2. Create branch: `git checkout -b feature/T<ID>-<name>`
3. Push with upstream tracking

**Acceptance Criteria**:
- Suggest next ID (max current ID + 1)
- Allow user input for task name
- Create and push branch automatically
- Output new branch name for confirmation

### R6: Constitution Alignment
These checks should be documented as development workflow requirements in `.specify/memory/constitution.md`.

**Acceptance Criteria**:
- "Development Workflow" section includes pre-implement checklist
- All checks are listed as mandatory before implementation
- Rationale explains why each check is necessary

---

## Success Criteria

- [ ] Automated pre-flight checks run before `/speckit-implement` begins
- [ ] All 5 checks (branch, develop ahead, merged detection, task inventory, new branch) execute successfully
- [ ] User is prompted only when action is required (merging, deleting, creating branch)
- [ ] Clear messaging: what was checked, what passed/failed, what action is needed
- [ ] Constitution updated to document this as standard workflow

---

## Scope Boundaries

### In Scope
- Pre-flight validation script (shell)
- Integration into `/speckit-implement` hook system
- Constitution documentation update

### Out of Scope
- Changes to speckit-implement core logic (focus only on pre-flight)
- Automatic force-merges or rebases (user must confirm)
- New CLI commands (use existing infrastructure)

---

## Dependencies & Assumptions

**Dependencies**:
- Git command available (`git --version`)
- `tasks.md` exists in feature directory
- `.specify/extensions.yml` exists for hook registration

**Assumptions**:
- User has sufficient git permissions to merge/delete branches
- Network access for `git fetch origin`
- Feature branches follow `feature/T<id>-*` naming after the fix

---

## Acceptance Scenarios

### Scenario 1: Normal Flow - All Tasks Complete
```
$ /speckit-implement
✓ Branch check: On feature/T104-improve-speckit-workflow
✓ Develop ahead: develop is 2 commits ahead
✓ No stale branches
✓ Task status: 5/5 completed
→ Create new feature branch for next task? (yes/no)
  > yes
  > Task ID [T105]: T105
  > Task name: enhance-error-handling
  > Created: feature/T105-enhance-error-handling
→ Proceeding with implementation...
```

### Scenario 2: Branch Needs Merge
```
$ /speckit-implement
✓ Branch check: On feature/T104-improve-speckit-workflow
⚠ Develop ahead: feature/T076-us3-etl-impl is 1 commit ahead
→ Merge feature/T076-us3-etl-impl into develop? (yes/no)
  > yes
  > Merged successfully
→ Continue with implementation? (yes/no)
  > yes
→ Proceeding with implementation...
```

### Scenario 3: On Master (Error)
```
$ /speckit-implement
✗ Branch check failed: Currently on master
ERROR: Must be on a feature branch (feature/T<id>-<name>)
Suggestion: Create a feature branch first with /speckit-git-feature
```

---

## Future Enhancements

- Detect and suggest task IDs from unfinished work
- Auto-rebase feature branches on develop instead of manual merge
- Integration with GitHub PR status (CI checks, reviews)
