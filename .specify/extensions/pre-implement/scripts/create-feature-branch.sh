#!/usr/bin/env bash
# R5: New feature branch creation - prompt for next task and create branch

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/git-helpers.sh"

validate_task_name() {
    local name="$1"

    # Check length
    if [[ ${#name} -lt 3 ]] || [[ ${#name} -gt 30 ]]; then
        print_error "Invalid task name length (must be 3-30 characters)" "Keep it concise"
        return 1
    fi

    # Check format: lowercase, hyphens allowed, no spaces
    if ! [[ "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
        print_error "Invalid task name format" "Use lowercase letters, numbers, and hyphens (e.g., improve-workflow)"
        return 1
    fi

    return 0
}

main() {
    # Fetch latest to see all branches
    if ! fetch_remote; then
        print_error "Failed to fetch from remote" "Cannot determine next task ID"
        return 1
    fi

    # Get max task ID
    local max_id=$(get_max_task_id)
    local next_id=$((max_id + 1))

    echo ""
    print_check pass "Ready to create new feature branch"
    echo "Current max task ID: T$max_id"
    echo "Suggested next ID:   T$next_id"
    echo ""

    # Prompt for task ID (optional override)
    printf "Task ID [T%d]: " "$next_id"
    read -r task_id_input
    local task_id="${task_id_input:-T$next_id}"

    # Validate task ID format
    if ! [[ "$task_id" =~ ^T[0-9]+$ ]]; then
        print_error "Invalid task ID format" "Use format like T105, T200, etc."
        return 1
    fi

    # Prompt for task name
    printf "Task name (short description): "
    read -r task_name

    # Validate task name
    if ! validate_task_name "$task_name"; then
        return 1
    fi

    # Create branch name
    local branch_name="feature/$task_id-$task_name"

    # Check if branch already exists
    if git rev-parse --verify "$branch_name" >/dev/null 2>&1; then
        print_error "Branch already exists: $branch_name" "Choose a different task ID or name"
        return 1
    fi

    # Create branch
    echo ""
    echo "Creating branch: $branch_name"
    if ! git checkout -b "$branch_name" 2>/dev/null; then
        print_error "Failed to create branch" "Check git installation and working directory"
        return 1
    fi

    # Push to remote with tracking
    echo "Pushing to remote..."
    if ! git push -u origin "$branch_name" 2>/dev/null; then
        print_error "Failed to push branch" "Check network connectivity and permissions"
        git checkout - >/dev/null 2>&1
        return 1
    fi

    if is_json_mode; then
        output_json "success" "Feature branch created" \
            "{\"branch\":\"$branch_name\",\"task_id\":\"$task_id\",\"task_name\":\"$task_name\"}"
    else
        print_check pass "Created feature branch: $branch_name"
        echo "Branch is tracking: origin/$branch_name"
    fi

    return 0
}

main "$@"
