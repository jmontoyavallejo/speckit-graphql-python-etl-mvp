#!/usr/bin/env bash
# Pre-flight checks orchestrator - runs all validation checks before implementation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
source "$SCRIPT_DIR/git-helpers.sh"

# Configuration
JSON_MODE=false
VERBOSE=false
SKIP_MERGE=false
SKIP_DELETE=false
SKIP_CREATE=false
FEATURE_DIR=""

# Results tracking
declare -a CHECK_RESULTS
declare -i PASSED_CHECKS=0
declare -i FAILED_CHECKS=0
declare -i WARNED_CHECKS=0

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --json)
                JSON_MODE=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --skip-merge)
                SKIP_MERGE=true
                shift
                ;;
            --skip-delete)
                SKIP_DELETE=true
                shift
                ;;
            --skip-create)
                SKIP_CREATE=true
                shift
                ;;
            --feature-dir)
                FEATURE_DIR="$2"
                shift 2
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

usage() {
    cat <<EOF
Usage: pre-flight-checks.sh [OPTIONS]

Options:
    --json              Output results in JSON format
    --verbose           Show detailed check information
    --skip-merge        Skip merge prompts for branches ahead of develop
    --skip-delete       Skip deletion prompts for stale branches
    --skip-create       Skip feature branch creation
    --feature-dir DIR   Path to feature directory (for task status check)
    --help              Show this help message

Examples:
    # Run all checks with defaults
    pre-flight-checks.sh

    # Run checks in JSON mode
    pre-flight-checks.sh --json

    # Skip merge prompts
    pre-flight-checks.sh --skip-merge

    # Check task status in specific directory
    pre-flight-checks.sh --feature-dir /path/to/feature
EOF
}

# Track individual check results
record_check() {
    local check_name="$1"
    local status="$2"
    local message="$3"

    case "$status" in
        pass)
            ((PASSED_CHECKS++))
            print_check pass "$check_name: $message"
            ;;
        warn)
            ((WARNED_CHECKS++))
            print_check warn "$check_name: $message"
            ;;
        fail)
            ((FAILED_CHECKS++))
            print_check fail "$check_name: $message"
            ;;
    esac
}

# Call individual check scripts
run_branch_status_check() {
    local check_script="$SCRIPT_DIR/check-branch-status.sh"

    if [[ ! -f "$check_script" ]]; then
        record_check "Branch Status" fail "Check script not found"
        return 1
    fi

    if bash "$check_script"; then
        record_check "Branch Status" pass "Valid feature branch"
        return 0
    else
        record_check "Branch Status" fail "Invalid branch format"
        return 1
    fi
}

run_develop_ahead_check() {
    local check_script="$SCRIPT_DIR/check-develop-ahead.sh"

    if [[ ! -f "$check_script" ]]; then
        record_check "Develop Ahead" fail "Check script not found"
        return 1
    fi

    if bash "$check_script" --skip-merge=$SKIP_MERGE; then
        record_check "Develop Ahead" pass "Develop is most ahead"
        return 0
    else
        record_check "Develop Ahead" warn "Some branches need merging"
        return 0  # Warn but don't fail
    fi
}

run_stale_branches_check() {
    local check_script="$SCRIPT_DIR/check-stale-branches.sh"

    if [[ ! -f "$check_script" ]]; then
        record_check "Stale Branches" fail "Check script not found"
        return 1
    fi

    if bash "$check_script" --skip-delete=$SKIP_DELETE; then
        record_check "Stale Branches" pass "No stale branches"
        return 0
    else
        record_check "Stale Branches" warn "Stale branches cleaned"
        return 0  # Warn but don't fail
    fi
}

run_task_status_check() {
    local check_script="$SCRIPT_DIR/check-task-status.sh"
    local feature_dir="${FEATURE_DIR:-.}"

    if [[ ! -f "$check_script" ]]; then
        record_check "Task Status" fail "Check script not found"
        return 1
    fi

    if bash "$check_script" --feature-dir "$feature_dir"; then
        record_check "Task Status" pass "All tasks completed"
        return 0
    else
        record_check "Task Status" warn "Some tasks pending"
        return 0  # Warn but don't fail
    fi
}

run_create_branch_check() {
    local check_script="$SCRIPT_DIR/create-feature-branch.sh"

    if [[ ! -f "$check_script" ]]; then
        record_check "New Branch" fail "Check script not found"
        return 1
    fi

    if [[ "$SKIP_CREATE" == "true" ]]; then
        print_check pass "Branch Creation: Skipped"
        return 0
    fi

    # Only prompt if all other checks passed
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        bash "$check_script" || true
        return 0
    fi

    return 0
}

# Generate summary report
generate_report() {
    local total=$((PASSED_CHECKS + WARNED_CHECKS + FAILED_CHECKS))

    if [[ "$JSON_MODE" == "true" ]]; then
        printf '{"summary":{"total":%d,"passed":%d,"warned":%d,"failed":%d},"status":"%s"}\n' \
            "$total" "$PASSED_CHECKS" "$WARNED_CHECKS" "$FAILED_CHECKS" \
            "$([ $FAILED_CHECKS -eq 0 ] && echo 'success' || echo 'failure')"
    else
        echo ""
        echo "================================"
        echo "Pre-Flight Check Summary"
        echo "================================"
        printf "Total Checks:  %d\n" "$total"
        printf "${GREEN}Passed:${NC}        %d\n" "$PASSED_CHECKS"
        printf "${YELLOW}Warnings:${NC}      %d\n" "$WARNED_CHECKS"
        printf "${RED}Failed:${NC}        %d\n" "$FAILED_CHECKS"
        echo "================================"

        if [[ $FAILED_CHECKS -eq 0 ]]; then
            print_check pass "All required checks passed"
            return 0
        else
            print_error "Some checks failed" "Review errors above and fix issues before proceeding"
            return 1
        fi
    fi
}

# Main execution
main() {
    parse_arguments "$@"

    if [[ "$VERBOSE" == "true" ]]; then
        echo "Running pre-flight checks..."
        echo "Current branch: $(get_current_branch)"
        echo "JSON mode: $JSON_MODE"
        echo ""
    fi

    # Run all checks
    run_branch_status_check || true
    run_develop_ahead_check || true
    run_stale_branches_check || true
    run_task_status_check || true
    run_create_branch_check || true

    # Generate and return report
    generate_report
}

main "$@"
