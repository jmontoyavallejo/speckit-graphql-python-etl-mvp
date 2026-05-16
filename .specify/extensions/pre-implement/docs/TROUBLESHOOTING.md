# Pre-Flight Checks Troubleshooting Guide

## Common Issues & Solutions

### "Not on a feature branch. Current branch: master"

**Cause**: You're on the master branch instead of a feature branch

**Quick Fix**:
```bash
git checkout -b feature/T<id>-<description>
/speckit-implement
```

**Prevention**: Always create and switch to feature branch before starting work

---

### "Invalid branch name: develop"

**Cause**: You're on develop branch; implementation must be on a feature branch

**Solution**:
```bash
# Create feature branch from current develop
git checkout -b feature/T<id>-<task-description>

# Or, create from master
git checkout master
git checkout -b feature/T<id>-<task-description>
```

---

### "Failed to fetch from remote"

**Cause**: Network issue, authentication problem, or invalid remote

**Diagnosis**:
```bash
# Test connectivity
git fetch origin --dry-run

# Check remotes are configured
git remote -v

# Check internet connection
ping github.com
```

**Solutions**:

1. **Network timeout**:
   ```bash
   # Increase timeout
   git config --global http.postBuffer 524288000
   git config --global core.compression 0
   ```

2. **Authentication failed**:
   ```bash
   # Refresh credentials
   git credential approve
   # Or re-authenticate
   gh auth login
   ```

3. **Invalid remote URL**:
   ```bash
   # Fix remote URL
   git remote set-url origin https://github.com/user/repo.git
   git remote -v  # Verify
   ```

---

### "Failed to merge feature/T103-... into develop"

**Cause**: Merge conflicts between branches

**Solution**:
```bash
# Abort current merge
git merge --abort

# Try merge with details
git merge --no-commit --no-ff feature/T103-old-feature

# Manually fix conflicts in your editor
# Look for markers: <<<<<<, ======, >>>>>>

# After fixing
git add .
git commit -m "Merge feature/T103: resolve conflicts"

# Return to implementation
/speckit-implement
```

**Prevent conflicts**:
- Keep feature branches short-lived
- Rebase on develop frequently
- Communicate with teammates about overlapping changes

---

### "Branch already exists: feature/T105-..."

**Cause**: Branch name is already taken

**Solution**:
```bash
# Option 1: Use different task ID
# Task ID [T105]: T106

# Option 2: Delete existing branch if merged
git branch -d feature/T105-old-version
/speckit-implement

# Option 3: Append suffix
# Task name: add-monitoring-v2
# Results in: feature/T105-add-monitoring-v2
```

---

### "Deleted X commits" warning during merge

**Cause**: Accidentally deleting commits from a branch

**Fix**:
```bash
# Don't commit yet; abort
git merge --abort

# Check branches for missing commits
git log feature/T104-improve-workflow

# Verify before merging
git diff develop feature/T104-improve-workflow
```

---

### "Permission denied: origin/feature/..."

**Cause**: Insufficient permissions to push to remote

**Check access**:
```bash
# Verify SSH key
ssh -T git@github.com

# List collaborators (if using GitHub)
gh repo view --json collaborators

# Check current user
git config user.name
git config user.email
```

**Solutions**:

1. **SSH key issue**:
   ```bash
   # Generate new SSH key
   ssh-keygen -t ed25519 -C "your-email@example.com"
   
   # Add to GitHub: Settings → SSH Keys
   ```

2. **HTTPS credential issue**:
   ```bash
   # Use personal access token
   git config --global user.email "your-email@example.com"
   git credential approve  # Re-enter credentials
   ```

---

### "tasks.md not found at ./tasks.md"

**Cause**: Running checks outside feature directory or before task generation

**Solution**:
```bash
# Generate tasks first
/speckit-tasks

# Or specify correct feature directory
bash .specify/extensions/pre-implement/scripts/check-task-status.sh \
  --feature-dir /path/to/feature/directory
```

---

### Checks timeout or hang

**Cause**: Network slowness or large number of branches

**Workaround**:
```bash
# Skip time-consuming checks
/speckit-implement --skip-merge --skip-delete

# Manual branch operations later
git fetch origin --prune  # Clean up remote refs
git branch -d feature/T102-old  # Delete manually
```

---

### "json_escape: command not found"

**Cause**: Older bash version missing function export

**Solution**:
```bash
# Update bash
# macOS
brew install bash

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install bash

# Verify version >= 4.0
bash --version
```

---

## Performance Issues

### Slow branch checks with many branches

**Problem**: Pre-flight checks take 30+ seconds with 100+ branches

**Solutions**:

1. **Clean up old branches**:
   ```bash
   # Delete all merged branches
   git branch --merged develop | grep -v develop | xargs git branch -d
   ```

2. **Prune remote tracking branches**:
   ```bash
   git fetch origin --prune
   ```

3. **Skip expensive checks**:
   ```bash
   /speckit-implement --skip-merge --skip-delete
   ```

---

### High CPU usage during checks

**Problem**: Pre-flight checks consuming high CPU

**Solution**:
```bash
# Monitor what's running
top -b -n 1 | head -20

# Kill if stuck
pkill -f pre-flight-checks.sh

# Run with verbose to see what's slow
/speckit-implement --verbose
```

---

## Debugging

### Enable verbose output
```bash
bash .specify/extensions/pre-implement/scripts/pre-flight-checks.sh --verbose
```

### Check logs
```bash
# View recent logs
tail -50 .specify/extensions/pre-implement/logs/run-*.log

# Follow live logs
tail -f .specify/extensions/pre-implement/logs/run-latest.log
```

### Test individual checks
```bash
# Test branch validation
bash .specify/extensions/pre-implement/scripts/check-branch-status.sh

# Test develop ahead check
bash .specify/extensions/pre-implement/scripts/check-develop-ahead.sh

# Test task status
bash .specify/extensions/pre-implement/scripts/check-task-status.sh

# Test branch creation
bash .specify/extensions/pre-implement/scripts/create-feature-branch.sh
```

### Run with debug shell
```bash
# Add set -x for debug output
bash -x .specify/extensions/pre-implement/scripts/pre-flight-checks.sh
```

---

## When to Skip Checks

### Safe to skip in these scenarios:

**Scenario**: Automated CI/CD pipeline
```bash
/speckit-implement --skip-merge --skip-delete --skip-create
```

**Scenario**: One-off fix on emergency hotfix
```bash
# Understand risks, then proceed
/speckit-implement --skip-merge --skip-delete
```

**Scenario**: Testing pre-flight system itself
```bash
# Manual checks without full orchestration
bash .specify/extensions/pre-implement/scripts/check-branch-status.sh
```

### Never skip these checks:

- **Branch Status**: Ensures you're on correct feature branch
- **Task Completion**: Prevents losing track of work
- **Develop Ahead**: Prevents merge conflicts later

---

## Getting Help

### Check documentation
- [WORKFLOW.md](./WORKFLOW.md) — Full workflow guide
- [EXAMPLES.md](./EXAMPLES.md) — Detailed examples

### Ask on team channels
- Slack: #dev-help or #git
- GitHub Issues: Create issue with logs

### Report bugs
Include in bug report:
```bash
# Get version
bash .specify/extensions/pre-implement/scripts/pre-flight-checks.sh --version

# Get logs
cat .specify/extensions/pre-implement/logs/run-*.log

# Get git state
git status
git log --oneline -5
git branch -a
```
