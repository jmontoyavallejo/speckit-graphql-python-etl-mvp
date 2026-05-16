#!/usr/bin/env bash
# R4: Task completion inventory - check tasks.md and report status

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

FEATURE_DIR="."

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --feature-dir)
                FEATURE_DIR="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
}

main() {
    parse_args "$@"

    local tasks_file="$FEATURE_DIR/tasks.md"

    # Check if tasks.md exists
    if [[ ! -f "$tasks_file" ]]; then
        if is_json_mode; then
            output_json "error" "tasks.md not found" "{\"path\":\"$tasks_file\"}"
        else
            print_error "tasks.md not found at $tasks_file" \
                "Run /speckit-tasks to generate task list first"
        fi
        return 1
    fi

    # Count completed and pending tasks
    local total=0
    local completed=0
    local pending=0

    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*\[([ X])\] ]]; then
            ((total++))
            if [[ "${BASH_REMATCH[1]}" == "X" ]]; then
                ((completed++))
            else
                ((pending++))
            fi
        fi
    done < "$tasks_file"

    # Calculate percentage
    local percentage=0
    if [[ $total -gt 0 ]]; then
        percentage=$((completed * 100 / total))
    fi

    if is_json_mode; {
        output_json "success" "Task status retrieved" \
            "{\"total\":$total,\"completed\":$completed,\"pending\":$pending,\"percentage\":$percentage}"
    else
        echo ""
        echo "Task Status: $completed/$total completed ($percentage%)"
        echo "  • Completed: $completed"
        echo "  • Pending:   $pending"
        echo ""

        if [[ $pending -eq 0 ]]; then
            print_check pass "All tasks completed!"
            return 0
        else
            print_check warn "$pending task(s) pending"
            if prompt_user "Proceed with implementation anyway?"; then
                return 0
            else
                return 1
            fi
        fi
    fi
}

main "$@"
