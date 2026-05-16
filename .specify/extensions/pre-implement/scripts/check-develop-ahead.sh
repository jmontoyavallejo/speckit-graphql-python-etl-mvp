#!/usr/bin/env bash
# R2: Develop branch ahead verification - ensure develop is most ahead

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
source "$(dirname "${BASH_SOURCE[0]}")/git-helpers.sh"

SKIP_MERGE=false

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --skip-merge=*)
                SKIP_MERGE="${1#*=}"
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

    # Fetch latest to ensure accurate comparison
    if ! fetch_remote; then
        print_error "Failed to fetch from remote" "Check network connectivity"
        return 1
    fi

    local ahead_branches=()
    local all_good=true

    # Check all feature branches
    for branch in $(git branch -r --format='%(refname:short)' 2>/dev/null | grep 'origin/feature/T'); do
        local local_branch="${branch#origin/}"
        local diff=$(get_commit_diff "$branch" "origin/develop")

        if [[ $diff -gt 0 ]]; then
            ahead_branches+=("$local_branch:$diff")
            all_good=false
        fi
    done

    if [[ "$all_good" == "true" ]]; then
        if is_json_mode; then
            output_json "success" "Develop is most ahead" "{\"ahead_branches\":[]}"
        else
            print_check pass "Develop branch is most ahead of all feature branches"
        fi
        return 0
    fi

    # Display branches that are ahead
    if [[ "$SKIP_MERGE" != "true" ]]; then
        echo ""
        print_check warn "The following branches are ahead of develop:"
        for branch_info in "${ahead_branches[@]}"; do
            local branch="${branch_info%:*}"
            local commits="${branch_info#*:}"
            echo "  • $branch (+$commits commits)"
        done
        echo ""

        if prompt_user "Merge stale branches into develop now?"; then
            for branch_info in "${ahead_branches[@]}"; do
                local branch="${branch_info%:*}"
                echo "Merging $branch into develop..."
                git checkout develop >/dev/null 2>&1
                if git merge "$branch" --no-edit >/dev/null 2>&1; then
                    print_check pass "Merged $branch"
                    git checkout - >/dev/null 2>&1
                else
                    print_error "Failed to merge $branch" "Resolve merge conflicts manually"
                    git checkout - >/dev/null 2>&1
                    return 1
                fi
            done
        else
            print_check warn "Skipped merge; branches remain ahead of develop"
        fi
    fi

    return 0
}

main "$@"
