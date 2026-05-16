# Pre-Flight Checks Examples

## Example 1: Normal Flow - All Checks Pass

**Scenario**: Starting implementation on a fresh feature branch with no conflicts

```bash
$ /speckit-implement

Checking prerequisites...
✓ Branch Status: Valid feature branch: feature/T104-improve-workflow [T104]
✓ Develop Ahead: Develop is most ahead of all feature branches
✓ Stale Branches: No stale branches found
✓ Task Status: 34/34 tasks completed (100%)
  → All tasks completed!
  → Create new feature branch for next task? (yes/no): no
  → Skipped new branch creation

================================
Pre-Flight Check Summary
================================
Total Checks:  4
✓ Passed:        4
⚠ Warnings:      0
✗ Failed:        0
================================
✓ All required checks passed
→ Proceeding with implementation...
```

---

## Example 2: Merge Required - Branch Ahead

**Scenario**: A feature branch is ahead of develop and needs merging

```bash
$ /speckit-implement

Checking prerequisites...
✓ Branch Status: Valid feature branch: feature/T104-improve-workflow
⚠ Develop Ahead: Found branches ahead of develop:
  • origin/feature/T103-fix-config (2 commits ahead)

The following branches are ahead of develop:
  • feature/T103-fix-config (+2 commits)

Merge stale branches into develop now? (yes/no): yes
Merging feature/T103-fix-config into develop...
✓ Merged feature/T103-fix-config
✓ Develop Ahead: Develop is now most ahead

✓ Stale Branches: No stale branches found
✓ Task Status: 20/34 tasks completed (59%)

Proceed with remaining tasks? (yes/no): yes

================================
Pre-Flight Check Summary
================================
Total Checks:  4
✓ Passed:        4
⚠ Warnings:      0
✗ Failed:        0
================================
✓ All required checks passed
→ Proceeding with implementation...
```

---

## Example 3: Error - On Master Branch

**Scenario**: Developer accidentally tries to implement on master

```bash
$ /speckit-implement

Checking prerequisites...
✗ Branch Status: Currently on master
ERROR: Must be on a feature branch (feature/T<id>-<name>)
Suggestion: Create one with: git checkout -b feature/T<id>-<name>

================================
Pre-Flight Check Summary
================================
Total Checks:  1
✓ Passed:        0
⚠ Warnings:      0
✗ Failed:        1
================================
✗ ERROR: Some checks failed
Review errors above and fix issues before proceeding

Exit code: 1
```

**Fix**:
```bash
# Create proper feature branch
git checkout -b feature/T104-improve-workflow

# Run checks again
/speckit-implement
```

---

## Example 4: Stale Branches Cleanup

**Scenario**: Previous work was merged, old branches need cleaning

```bash
$ /speckit-implement

Checking prerequisites...
✓ Branch Status: Valid feature branch: feature/T104-improve-workflow
✓ Develop Ahead: Develop is most ahead

⚠ Stale Branches: Found 3 stale branch(es):
  • feature/T098-old-feature
  • feature/T099-completed-work
  • feature/T102-merged-changes

Delete stale branches? (yes/no): yes
Deleting feature/T098-old-feature...
✓ Deleted feature/T098-old-feature
✓ Deleted remote: origin/feature/T098-old-feature
Deleting feature/T099-completed-work...
✓ Deleted feature/T099-completed-work
✓ Deleted remote: origin/feature/T099-completed-work
Deleting feature/T102-merged-changes...
✓ Deleted feature/T102-merged-changes
✓ Deleted remote: origin/feature/T102-merged-changes

✓ Task Status: 34/34 tasks completed (100%)

================================
Pre-Flight Check Summary
================================
Total Checks:  5
✓ Passed:        5
⚠ Warnings:      0
✗ Failed:        0
================================
✓ All required checks passed
→ Proceeding with implementation...
```

---

## Example 5: Create New Feature Branch for Next Task

**Scenario**: All current tasks complete, ready to start new work

```bash
$ /speckit-implement

Checking prerequisites...
✓ Branch Status: Valid feature branch: feature/T104-improve-workflow
✓ Develop Ahead: Develop is most ahead
✓ Stale Branches: No stale branches found
✓ Task Status: 34/34 tasks completed (100%)
  → All tasks completed!

Ready to create new feature branch
Current max task ID: T104
Suggested next ID:   T105

Task ID [T105]: T105
Task name (short description): add-monitoring-metrics

Creating branch: feature/T105-add-monitoring-metrics
Pushing to remote...
✓ Created feature branch: feature/T105-add-monitoring-metrics
Branch is tracking: origin/feature/T105-add-monitoring-metrics

================================
Pre-Flight Check Summary
================================
Total Checks:  5
✓ Passed:        5
⚠ Warnings:      0
✗ Failed:        0
================================
✓ All required checks passed
→ Proceeding with implementation...
```

---

## Example 6: Pending Tasks - Prompt to Proceed

**Scenario**: Not all tasks are complete yet

```bash
$ /speckit-implement

Checking prerequisites...
✓ Branch Status: Valid feature branch: feature/T104-improve-workflow
✓ Develop Ahead: Develop is most ahead
✓ Stale Branches: No stale branches found

Task Status: 15/34 completed (44%)
  • Completed: 15
  • Pending:   19

Proceed with implementation anyway? (yes/no): yes

================================
Pre-Flight Check Summary
================================
Total Checks:  4
✓ Passed:        4
⚠ Warnings:      0
✗ Failed:        0
================================
✓ All required checks passed
→ Proceeding with implementation...
```

---

## Example 7: JSON Output Mode

**Scenario**: Scripting or CI/CD integration

```bash
$ /speckit-implement --json

{"status":"success","message":"Valid feature branch","data":{"branch":"feature/T104-improve-workflow","task_id":"T104"}}
{"status":"success","message":"Develop is most ahead","data":{"ahead_branches":[]}}
{"status":"success","message":"No stale branches","data":{"merged_branches":[]}}
{"summary":{"total":4,"passed":4,"warned":0,"failed":0},"status":"success"}
```

**Parsing with jq**:
```bash
# Check if all passed
/speckit-implement --json | jq '.summary.failed == 0'

# Get task ID
/speckit-implement --json | jq '.data.task_id'

# Extract branch name
/speckit-implement --json | jq '.data.branch'
```

---

## Example 8: Custom Options

**Scenario**: Skip merges for manual review

```bash
$ /speckit-implement --skip-merge --skip-delete --feature-dir ./specs/T104

✓ Branch Status: Valid feature branch
⚠ Develop Ahead: Found 1 branch ahead, merge skipped (--skip-merge)
⚠ Stale Branches: Found 2 merged branches, deletion skipped (--skip-delete)
✓ Task Status: 20/34 tasks completed

Note: Use manual commands to handle skipped actions:
  git merge feature/T103-...
  git branch -d feature/T102-...
```

---

## Common Patterns

### Pattern 1: Daily Development Loop
```bash
# Morning: Check everything before starting
/speckit-implement

# Work on tasks...

# Before commit: Ensure clean state
/speckit-implement --verbose

# When done: Create next task branch
/speckit-implement
```

### Pattern 2: Code Review / Pull Request
```bash
# Before submitting PR
/speckit-implement --verbose

# Merge to develop (if approved)
git checkout develop
git merge feature/T104-improve-workflow

# Clean up merged branch
/speckit-implement
```

### Pattern 3: Continuous Integration
```bash
# In CI/CD pipeline
if ! /speckit-implement --json | jq -e '.summary.failed == 0'; then
    echo "Pre-flight checks failed"
    exit 1
fi

# Proceed with tests, build, etc.
./run-tests.sh
```

---

## Tips & Tricks

### Skip confirmations in automated contexts
```bash
/speckit-implement --skip-merge --skip-delete --skip-create
```

### Get detailed debug information
```bash
/speckit-implement --verbose 2>&1 | tee pre-flight-debug.log
```

### Check only specific component
```bash
# Branch validation only
bash .specify/extensions/pre-implement/scripts/check-branch-status.sh

# Task status only
bash .specify/extensions/pre-implement/scripts/check-task-status.sh \
  --feature-dir ./specs/T104
```

### Manual branch operations
```bash
# Check which branches are merged
git branch --merged develop

# Manually merge a branch
git merge feature/T103-fix

# Manually delete merged branch
git branch -d feature/T102-old
```
