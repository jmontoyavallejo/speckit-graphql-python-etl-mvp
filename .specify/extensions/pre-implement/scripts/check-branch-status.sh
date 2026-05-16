#!/usr/bin/env bash
# R1: Pre-flight branch status check - validate feature branch naming

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/git-helpers.sh"

main() {
    local current_branch=$(get_current_branch)

    # Must be on a feature branch, not master or develop
    case "$current_branch" in
        master|develop|main)
            print_error "Currently on $current_branch" \
                "Must be on a feature branch (feature/T<id>-<name>). Create one with: git checkout -b feature/T<id>-<name>"
            return 1
            ;;
    esac

    # Validate feature branch naming pattern: feature/T<digits>-<name>
    if ! [[ "$current_branch" =~ ^feature/T[0-9]+- ]]; then
        print_error "Invalid branch name: $current_branch" \
            "Feature branches must follow gitflow convention: feature/T<id>-<name> (e.g., feature/T104-improve-workflow)"
        return 1
    fi

    # Extract task ID
    local task_id=$(echo "$current_branch" | grep -oE 'T[0-9]+' | head -1)

    if is_json_mode; then
        output_json "success" "Valid feature branch" "{\"branch\":\"$current_branch\",\"task_id\":\"$task_id\"}"
    else
        print_check pass "Valid feature branch: $current_branch [$task_id]"
    fi

    return 0
}

main "$@"
