#!/usr/bin/env bash
# R3: Auto-merge stale feature branches - detect and offer to delete merged branches

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/git-helpers.sh"

SKIP_DELETE=false

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --skip-delete=*)
                SKIP_DELETE="${1#*=}"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
}

main() {
    parse_args "$@"

    # Fetch latest
    if ! fetch_remote; then
        print_error "Failed to fetch from remote" "Check network connectivity"
        return 1
    fi

    local merged_branches=()
    local current_branch=$(get_current_branch)

    # Find all merged branches
    for branch in $(git branch --merged develop --format='%(refname:short)' 2>/dev/null); do
        # Skip master, develop, main, and current branch
        if [[ ! "$branch" =~ ^(master|develop|main)$ ]] && [[ "$branch" != "$current_branch" ]]; then
            merged_branches+=("$branch")
        fi
    done

    if [[ ${#merged_branches[@]} -eq 0 ]]; then
        if is_json_mode; then
            output_json "success" "No stale branches" "{\"merged_branches\":[]}"
        else
            print_check pass "No stale branches found"
        fi
        return 0
    fi

    # Prompt to delete merged branches
    if [[ "$SKIP_DELETE" != "true" ]]; then
        echo ""
        print_check warn "Found ${#merged_branches[@]} stale branch(es):"
        for branch in "${merged_branches[@]}"; do
            echo "  • $branch"
        done
        echo ""

        if prompt_user "Delete stale branches?"; then
            for branch in "${merged_branches[@]}"; do
                if delete_branch "$branch"; then
                    print_check pass "Deleted $branch"
                    # Also delete remote if it exists
                    if git rev-parse "origin/$branch" >/dev/null 2>&1; then
                        git push origin --delete "$branch" >/dev/null 2>&1
                        print_check pass "Deleted remote: origin/$branch"
                    fi
                else
                    print_error "Failed to delete $branch" "May have unpushed commits"
                fi
            done
        else
            print_check warn "Skipped deletion; branches remain"
        fi
    else
        print_check warn "Found ${#merged_branches[@]} stale branch(es), deletion skipped"
    fi

    return 0
}

main "$@"
