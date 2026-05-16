# Pre-Implementation Workflow Guide

## Overview

The pre-implement workflow provides automated validation that ensures your repository is in a consistent state before beginning implementation. It runs 5 essential checks to catch issues early.

## Pre-Flight Checks

### 1. Branch Status Check ✓ | ⚠ | ✗

**Purpose**: Validates that you're on a valid feature branch

**What it checks**:
- Current branch name follows gitflow convention: `feature/T<id>-<name>`
- Not on master, develop, or main branches
- Extracts task ID from branch name

**Success**: ✓ Valid feature branch: feature/T104-improve-workflow

**Failure**: ✗ Invalid branch format or on protected branches

**How to fix**:
```bash
# Create proper feature branch
git checkout -b feature/T<id>-<description>

# Example:
git checkout -b feature/T104-improve-workflow
```

---

### 2. Develop Branch Ahead Verification ✓ | ⚠

**Purpose**: Ensures `develop` branch is the most ahead of all feature branches

**What it checks**:
- Fetches latest from remote
- Compares commit counts between develop and all feature branches
- Identifies any branches that are ahead of develop

**Success**: ✓ Develop branch is most ahead of all feature branches

**Warning**: ⚠ Found 1 branch ahead of develop by 3 commits

**When it warns**:
- Feature branch has commits not yet merged to develop
- Often happens when develop receives updates while you're coding

**What happens**:
- You're prompted to merge the stale branch
- If you accept, the branch is merged into develop
- Your current branch is preserved (switches back automatically)

---

### 3. Stale Branches Cleanup ✓ | ⚠

**Purpose**: Detects and offers to delete branches that are already merged

**What it checks**:
- Finds branches that have been fully merged into develop
- Excludes: master, develop, main, and current branch
- Lists each stale branch for review

**Success**: ✓ No stale branches found

**Warning**: ⚠ Found 2 stale branches

**What happens**:
- You're shown list of merged branches
- Prompted to delete them
- Deleted from both local and remote

**Why**: Keeping merged branches around creates confusion about which work is ongoing

---

### 4. Task Completion Inventory ✓ | ⚠

**Purpose**: Shows task completion status and prompts for remaining work

**What it checks**:
- Reads `tasks.md` from feature directory
- Counts completed tasks (marked `[X]`)
- Counts pending tasks (marked `[ ]`)
- Calculates completion percentage

**Success**: ✓ All tasks completed (34/34)

**Warning**: ⚠ Task status: 20/34 completed (59%)

**What happens**:
- If all tasks complete: Proceeds to branch creation
- If tasks pending: Asks "Proceed with implementation anyway?"
  - **yes**: Continues with new branch creation
  - **no**: Halts and returns to work

---

### 5. New Feature Branch Creation (Optional) ✓

**Purpose**: Guides you through creating the next feature branch for continued work

**When triggered**:
- All previous checks passed
- All tasks in current feature complete
- User confirms and is ready for next work item

**What it does**:
1. Suggests next task ID (current max + 1)
   ```
   Current max task ID: T104
   Suggested next ID:   T105
   ```

2. Prompts for task name
   ```
   Task name (short description): enhance-error-handling
   ```

3. Creates and pushes new branch
   ```
   git checkout -b feature/T105-enhance-error-handling
   git push -u origin feature/T105-enhance-error-handling
   ```

4. Confirms tracking setup
   ```
   ✓ Created feature branch: feature/T105-enhance-error-handling
   Branch is tracking: origin/feature/T105-enhance-error-handling
   ```

**Task name requirements**:
- 3-30 characters long
- Lowercase letters, numbers, hyphens only
- No spaces
- Examples: `add-logging`, `fix-edge-cases`, `improve-performance`

---

## Running Pre-Flight Checks

### Automatic (via speckit-implement)

```bash
/speckit-implement
```

Pre-flight checks run automatically before implementation begins.

### Manual

```bash
# Run all checks with defaults
bash .specify/extensions/pre-implement/scripts/pre-flight-checks.sh

# Run with specific feature directory
bash .specify/extensions/pre-implement/scripts/pre-flight-checks.sh --feature-dir /path/to/feature

# Skip interactive prompts
bash .specify/extensions/pre-implement/scripts/pre-flight-checks.sh --skip-merge --skip-delete

# JSON output for scripting
bash .specify/extensions/pre-implement/scripts/pre-flight-checks.sh --json

# Verbose output for debugging
bash .specify/extensions/pre-implement/scripts/pre-flight-checks.sh --verbose
```

---

## Command Line Options

| Option | Effect |
|--------|--------|
| `--json` | Output results in machine-readable JSON format |
| `--verbose` | Show detailed check information |
| `--skip-merge` | Skip merge prompts for branches ahead of develop |
| `--skip-delete` | Skip deletion prompts for stale branches |
| `--skip-create` | Skip feature branch creation |
| `--feature-dir DIR` | Specify path to feature directory for task checks |
| `--help` | Show help message |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All checks passed; proceed with implementation |
| `1` | One or more critical checks failed; fix before proceeding |

---

## Success Scenarios

### Scenario 1: Fresh Start
```
✓ Branch Status: Valid feature branch: feature/T105-new-feature
✓ Develop Ahead: Develop is most ahead
✓ Stale Branches: No stale branches found
✓ Task Status: No pending tasks (or new feature)
→ Ready for implementation
```

### Scenario 2: All Tasks Done
```
✓ Branch Status: Valid feature branch: feature/T104-improve-workflow
✓ Develop Ahead: Develop is most ahead
✓ Stale Branches: No stale branches found
✓ Task Status: 34/34 tasks completed
→ Create new feature branch for next task?
  [Creates feature/T105-...]
```

### Scenario 3: Need Merge
```
✓ Branch Status: Valid feature branch
⚠ Develop Ahead: 1 branch ahead by 3 commits
  Found: feature/T103-old-work
  Merge into develop? (yes/no): yes
  Merged successfully
→ Continue with implementation
```

---

## Troubleshooting

### "Not on a feature branch" Error

**Problem**: You're on master, develop, or a non-conforming branch

**Solution**:
```bash
# Create proper feature branch
git checkout -b feature/T<id>-<name>

# Then run checks again
/speckit-implement
```

### "Failed to fetch from remote" Error

**Problem**: Network issue or authentication problem

**Solution**:
```bash
# Test connectivity
git fetch origin

# Check credentials
git config --list | grep credential

# If needed, authenticate
git credential fill
```

### "Failed to merge branch" Error

**Problem**: Merge conflicts prevent auto-merge

**Solution**:
```bash
# Resolve conflicts manually
git merge <branch>
# Fix conflicts in editor
git add .
git commit -m "Merge: resolve conflicts"

# Then restart checks
/speckit-implement
```

---

## Related Documentation

- [EXAMPLES.md](./EXAMPLES.md) — Detailed walkthrough examples
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) — Common issues and solutions
- [Constitution](../../.specify/memory/constitution.md#pre-implementation-workflow) — Project policies and standards
