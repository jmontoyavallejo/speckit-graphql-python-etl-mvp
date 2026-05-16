#!/usr/bin/env bash
# Git integration helpers for pre-flight checks

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

# Get current branch name safely
get_current_branch() {
    git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown"
}

# Get remote tracking branch
get_remote_tracking_branch() {
    local branch="${1:-$(get_current_branch)}"
    git rev-parse --abbrev-ref "$branch@{upstream}" 2>/dev/null || echo ""
}

# Safely fetch from remote
fetch_remote() {
    local remote="${1:-origin}"

    if ! git fetch "$remote" --quiet 2>/dev/null; then
        print_error "Failed to fetch from $remote" "Check network connectivity and remote access"
        return 1
    fi

    return 0
}

# Get all branches (local and remote)
get_all_branches() {
    local branch_type="${1:-all}"  # all, local, remote

    case "$branch_type" in
        local)
            git branch --format='%(refname:short)' 2>/dev/null
            ;;
        remote)
            git branch -r --format='%(refname:short)' 2>/dev/null | grep -v HEAD
            ;;
        *)
            (
                git branch --format='%(refname:short)' 2>/dev/null
                git branch -r --format='%(refname:short)' 2>/dev/null | grep -v HEAD
            ) | sort | uniq
            ;;
    esac
}

# Get commit count between two branches
get_commit_diff() {
    local from_branch="$1"
    local to_branch="$2"

    if ! git rev-parse "$from_branch" >/dev/null 2>&1 || ! git rev-parse "$to_branch" >/dev/null 2>&1; then
        echo "0"
        return 1
    fi

    git rev-list --count "$from_branch..$to_branch" 2>/dev/null || echo "0"
}

# Check if branch is merged into another
is_branch_merged() {
    local branch="$1"
    local target="${2:-develop}"

    if git merge-base --is-ancestor "$branch" "$target" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Delete a branch safely
delete_branch() {
    local branch="$1"
    local force="${2:-false}"

    if [[ "$force" == "true" ]]; then
        git branch -D "$branch" 2>/dev/null && return 0
    else
        git branch -d "$branch" 2>/dev/null && return 0
    fi

    return 1
}

# Get max task ID from branches
get_max_task_id() {
    local max_id=0
    local branch

    for branch in $(git branch --format='%(refname:short)' 2>/dev/null); do
        # Extract T<id> from branch name
        if [[ "$branch" =~ T([0-9]+) ]]; then
            local id="${BASH_REMATCH[1]}"
            if ((id > max_id)); then
                max_id=$id
            fi
        fi
    done

    echo $max_id
}

# Validate branch name format
validate_branch_name() {
    local branch="$1"

    # Must be feature/T<id>-<name>
    if [[ "$branch" =~ ^feature/T[0-9]+-[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
        return 0
    else
        return 1
    fi
}

export -f get_current_branch get_remote_tracking_branch fetch_remote
export -f get_all_branches get_commit_diff is_branch_merged delete_branch
export -f get_max_task_id validate_branch_name
