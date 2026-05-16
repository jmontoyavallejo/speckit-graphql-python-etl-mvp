---
description: "Task breakdown for improved speckit-implement workflow with automated pre-flight checks"
---

# Tasks: Improve Speckit Implement Workflow

**Input**: Design documents from `/specs/T104-improve-speckit-workflow/`

**Prerequisites**: spec.md (required), plan.md (required)

**Tests**: Optional; focus on shell script validation and integration testing

---

## Phase 1: Setup (Infrastructure & Script Foundation)

**Purpose**: Create script infrastructure and directory structure for pre-flight checks

- [ ] T001 Create `.specify/extensions/pre-implement/` directory structure for pre-flight scripts
- [ ] T002 Create `.specify/extensions/pre-implement/scripts/` directory for shell scripts
- [ ] T003 Create `.specify/extensions/pre-implement/templates/` for pre-flight check templates
- [ ] T004 [P] Create `.specify/extensions/pre-implement/README.md` documenting pre-flight check system
- [ ] T005 [P] Set up logging directory `.specify/extensions/pre-implement/logs/` with .gitkeep

**Checkpoint**: Directory structure ready, shell script infrastructure in place.

---

## Phase 2: Foundational (Core Pre-Flight Check Script)

**Purpose**: Build the main orchestration script that runs all pre-flight checks sequentially

- [ ] T006 Create `.specify/extensions/pre-implement/scripts/pre-flight-checks.sh` master script with:
  - Command-line argument parsing (--json, --verbose, --skip-merge, --skip-delete)
  - Error handling and exit codes
  - Logging setup to `.specify/extensions/pre-implement/logs/run-$(date).log`
  - Main execution loop calling individual check functions

- [ ] T007 [P] Create `.specify/extensions/pre-implement/scripts/common.sh` utility functions:
  - `print_check()` — formatted output for each check (✓, ⚠, ✗)
  - `print_error()` — error messages with suggestions
  - `prompt_user()` — interactive yes/no prompts
  - `run_git_command()` — safe git wrapper with error handling
  - JSON output formatting for integration

- [ ] T008 [P] Add git integration wrapper in `.specify/extensions/pre-implement/scripts/git-helpers.sh`:
  - `get_current_branch()` — safely get current branch name
  - `get_remote_tracking_branch()` — detect upstream tracking
  - `fetch_remote()` — safe `git fetch origin` with error handling

**Checkpoint**: Master script and utility functions ready for individual checks.

---

## Phase 3: Core Implementation (Individual Pre-Flight Checks)

**Purpose**: Implement each of the 5 required pre-flight validation checks

### R1: Pre-Flight Branch Status Check

- [ ] T009 Create `.specify/extensions/pre-implement/scripts/check-branch-status.sh`:
  - Get current branch: `git rev-parse --abbrev-ref HEAD`
  - Validate branch pattern: `feature/T[0-9]+.*`
  - Output: Branch name, validation status, error message if invalid
  - Exit code: 0 on valid feature branch, 1 on invalid
  - Handles: master, develop, and unrecognized branches with appropriate error messages

- [ ] T010 [P] Test branch validation with:
  - Valid branches: `feature/T001-test`, `feature/T104-improve-speckit-workflow`
  - Invalid branches: `master`, `develop`, `feature/invalid`, `T001-no-prefix`
  - Error messages clear and actionable

### R2: Develop Branch Ahead Verification

- [ ] T011 Create `.specify/extensions/pre-implement/scripts/check-develop-ahead.sh`:
  - Run: `git fetch origin --quiet`
  - Get all branches: `git branch -r | grep feature`
  - For each branch, calculate: `git rev-list --count <branch>..develop`
  - Compare all counts, determine which (if any) are ahead of develop
  - Output table: Branch name, commit count diff, status
  - Suggest merge or rebase for ahead branches

- [ ] T012 [P] Test develop ahead check:
  - With develop most ahead (expected): Show green ✓
  - With feature branch ahead: Show warning ⚠, prompt to merge
  - With multiple branches: Show status for all, suggest merge order

### R3: Auto-Merge Stale Feature Branches (Optional)

- [ ] T013 Create `.specify/extensions/pre-implement/scripts/check-stale-branches.sh`:
  - Detect merged branches: `git branch --merged develop`
  - Filter out master, develop, current branch
  - For each merged branch, prompt: "Branch X is merged into develop. Delete? (yes/no)"
  - Execute: `git branch -d <merged-branch>` if confirmed
  - Output: Deleted branch count, remaining stale branches

- [ ] T014 [P] Test stale branch detection:
  - With merged branches: Correctly identify and prompt for deletion
  - With clean branches: Show "No stale branches found"
  - Deletion confirmation and execution

### R4: Task Completion Inventory

- [ ] T015 Create `.specify/extensions/pre-implement/scripts/check-task-status.sh`:
  - Read tasks.md from FEATURE_DIR (passed as argument)
  - Parse checklist syntax: Count `- [X]` and `- [ ]` lines
  - Calculate: Total, Completed, Pending counts
  - Output format: "Task Status: 103/103 completed | Pending: 0"
  - If pending tasks exist, prompt: "Proceed with remaining tasks? (yes/no)"
  - Exit code: 0 on proceed, 1 on cancel

- [ ] T016 [P] Test task counting:
  - With all tasks complete: Show green ✓, exit 0
  - With pending tasks: Show warning ⚠, require user confirmation
  - Parse different task formats (multiple checkboxes, mixed completion)

### R5: New Feature Branch Creation (If All Tasks Done)

- [ ] T017 Create `.specify/extensions/pre-implement/scripts/create-feature-branch.sh`:
  - Detect next task ID: Parse existing branches, find max T<ID>, add 1
  - Suggest: "Next task ID [T105]:"
  - Prompt: "Task name (short description):"
  - Validate task name: No spaces, lowercase, 3-30 characters
  - Create branch: `git checkout -b feature/T<ID>-<name>`
  - Push: `git push -u origin feature/T<ID>-<name>`
  - Output confirmation: "Created feature/T<ID>-<name> (tracking origin)"

- [ ] T018 [P] Test branch creation:
  - With suggested ID and name: Create and push successfully
  - With invalid name: Prompt for correction
  - With existing branch: Handle gracefully, suggest different ID
  - Push verification (tracking upstream)

---

## Phase 4: Integration & Orchestration

**Purpose**: Integrate pre-flight checks into speckit-implement workflow and extension hooks

- [ ] T019 Update pre-flight-checks.sh to orchestrate all checks:
  - Call check-branch-status.sh
  - Call check-develop-ahead.sh
  - Call check-stale-branches.sh (optional, skip with --skip-delete)
  - Call check-task-status.sh with FEATURE_DIR
  - If all tasks complete, call create-feature-branch.sh (optional, skip with --skip-create)
  - Aggregate results: Pass/Warn/Fail status for each check
  - JSON output: Summary of all checks

- [ ] T020 [P] Create `.specify/extensions/pre-implement/hooks/before-implement.sh`:
  - Hook entry point called by speckit-implement pre-flight
  - Parses FEATURE_DIR from environment or arguments
  - Calls pre-flight-checks.sh with appropriate flags
  - Returns aggregated exit code: 0 (continue), 1 (abort)
  - Handles errors gracefully without stopping speckit-implement

- [ ] T021 [P] Register hook in `.specify/extensions.yml`:
  - Add entry under `hooks.before_implement`:
    - Extension: pre-implement
    - Command: pre-implement.before-implement
    - Enabled: true
    - Optional: false (make it mandatory)
    - Description: "Run pre-flight checks before implementation"

- [ ] T022 Test hook integration:
  - Hook executes via speckit extension system
  - Pre-flight checks run automatically before implementation
  - User is prompted only when action required (merge, delete, create branch)
  - Implementation proceeds if all checks pass

---

## Phase 5: Documentation & Constitution Update

**Purpose**: Document workflow in code and project governance

- [ ] T023 Create `.specify/extensions/pre-implement/docs/WORKFLOW.md`:
  - Overview of pre-flight check system
  - Each check: purpose, what it validates, user prompts
  - Success and failure scenarios
  - Troubleshooting guide

- [ ] T024 [P] Update `specs/001-graphql-python-etl/.specify/memory/constitution.md`:
  - Add section: "Pre-Implementation Workflow (T104)"
  - Document 5 required checks as mandatory policy
  - Explain rationale for each check
  - Include example output for users to recognize
  - Cross-reference with git flow branching model section

- [ ] T025 [P] Create `.specify/extensions/pre-implement/docs/EXAMPLES.md`:
  - Example 1: Normal flow (all checks pass)
  - Example 2: Merge required (develop behind)
  - Example 3: Error on master branch
  - Example 4: Pending tasks, prompt to proceed
  - Example 5: All done, create new feature branch

- [ ] T026 Update project README.md:
  - Add section: "Pre-Implementation Validation"
  - Briefly explain automatic pre-flight checks
  - Link to `.specify/extensions/pre-implement/docs/WORKFLOW.md` for details

**Checkpoint**: All workflows documented, constitution updated.

---

## Phase 6: Polish & Validation

**Purpose**: Test end-to-end, ensure reliability, document edge cases

- [ ] T027 [P] Integration test: Full pre-flight check workflow:
  - Execute pre-flight-checks.sh on valid feature branch
  - Verify all 5 checks execute
  - Verify JSON output format
  - Verify exit codes

- [ ] T028 [P] Edge case testing:
  - Test on branch with no tracking: `feature/T999-orphan` (not pushed)
  - Test with dirty working tree (uncommitted changes)
  - Test with merge conflicts in progress
  - Test on detached HEAD
  - Test with shallow clone

- [ ] T029 Create `.specify/extensions/pre-implement/TROUBLESHOOTING.md`:
  - Common issues: network errors, permission denied, branch conflicts
  - Solutions: Retry commands, reset local branch, force push
  - Debug flag: `--verbose` for detailed output

- [ ] T030 [P] Test logging:
  - Verify all checks produce log entries
  - Check log file location and format
  - Verify log rotation (if applicable)
  - Test with `--json` flag for machine-readable output

- [ ] T031 Final validation: Manual walkthrough
  - Test on current working setup (T104 branch)
  - Verify each check output matches spec
  - Confirm user prompts are clear and actionable
  - Test merge, delete, and branch creation flows

---

## Phase 7: Cleanup & Ready for Production

**Purpose**: Final polish, code review readiness, deployment

- [ ] T032 Code review preparation:
  - Ensure all shell scripts have proper shebang (#/bin/bash)
  - Add comments for complex logic
  - Verify error handling covers edge cases
  - Check for hardcoded paths (should use variables)

- [ ] T033 [P] Performance validation:
  - Measure execution time for pre-flight checks (should be < 5 seconds)
  - Optimize git commands (use --quiet, avoid redundant calls)
  - Test with large monorepo (many branches)

- [ ] T034 Create `.specify/extensions/pre-implement/VERSION`:
  - Version: 1.0.0
  - Compatibility: speckit-implement >= 4.0.0

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. Start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion.
- **Core Implementation (Phase 3)**: Depends on Foundational completion. Each check is independent after Phase 2.
- **Integration (Phase 4)**: Depends on all Phase 3 checks being complete.
- **Documentation (Phase 5)**: Can run in parallel with Phase 4 after Phase 3 is complete.
- **Polish (Phase 6)**: Depends on Integration completion.
- **Cleanup (Phase 7)**: Final phase after all testing complete.

### Within Phases

- **Phase 1**: All tasks [P] can run in parallel (different files)
- **Phase 2**: T007-T008 [P] can run in parallel; T006 sequentially (depends on common.sh)
- **Phase 3**: Individual check creation tasks are independent:
  - R1 (T009-T010): Independent
  - R2 (T011-T012): Independent
  - R3 (T013-T014): Independent
  - R4 (T015-T016): Independent
  - R5 (T017-T018): Independent
  - All can run in parallel [P]
- **Phase 4**: T019 (orchestrator) must complete before T020-T022
- **Phase 5**: T024-T025 [P] can run in parallel; T026 sequentially (updates README)
- **Phase 6**: Testing tasks T027-T028 [P] can run in parallel
- **Phase 7**: Final code review and cleanup

### Parallel Execution Example

**Parallel Block 1** (Phase 2, utilities):
```
- T007: Create common.sh
- T008: Create git-helpers.sh
```

**Parallel Block 2** (Phase 3, individual checks):
```
- T009: Branch status check script
- T011: Develop ahead check script
- T013: Stale branches check script
- T015: Task status check script
- T017: Branch creation script
```

**Parallel Block 3** (Phase 5, documentation):
```
- T024: Update constitution
- T025: Create examples doc
```

---

## Implementation Strategy

### MVP Scope (v1.0 - Ready for Use)

Complete all of Phases 1-4 to have a working pre-flight check system integrated into speckit-implement.

**Essential tasks** (MVP):
- T001-T005: Setup infrastructure
- T006-T008: Core orchestration script
- T009-T018: All 5 pre-flight checks
- T019-T022: Integration into speckit-implement

**Time estimate**: 4-6 hours for experienced developer

### Incremental Enhancements

**Phase 5 (v1.0+1)**: Documentation ensures team adoption

**Phase 6-7 (v1.1)**: Edge case handling and performance optimization

---

## Success Criteria

- [ ] All 5 pre-flight checks execute without errors
- [ ] Pre-flight checks integrate seamlessly with `/speckit-implement`
- [ ] User prompts are clear and actionable
- [ ] JSON output mode for machine integration
- [ ] Constitution updated to document mandatory workflow
- [ ] All edge cases handled gracefully
- [ ] Logging enables debugging of issues
- [ ] Performance < 5 seconds for full pre-flight sequence
