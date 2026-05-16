#!/usr/bin/env bash
# Common utility functions for pre-flight checks

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print formatted check result
print_check() {
    local status="$1"
    local message="$2"

    case "$status" in
        pass)
            printf "${GREEN}✓${NC} %s\n" "$message"
            ;;
        warn)
            printf "${YELLOW}⚠${NC} %s\n" "$message"
            ;;
        fail)
            printf "${RED}✗${NC} %s\n" "$message"
            ;;
        *)
            printf "  %s\n" "$message"
            ;;
    esac
}

# Print error message with context
print_error() {
    local message="$1"
    local suggestion="$2"

    printf "${RED}ERROR:${NC} %s\n" "$message" >&2
    if [[ -n "$suggestion" ]]; then
        printf "Suggestion: %s\n" "$suggestion" >&2
    fi
}

# Prompt user for yes/no response
prompt_user() {
    local prompt="$1"
    local default="${2:-no}"

    printf "%s (yes/no) [default: %s]: " "$prompt" "$default"
    read -r response
    response="${response:-$default}"

    case "$response" in
        yes|y|YES|Y)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Safe git command wrapper with error handling
run_git_command() {
    local cmd=("$@")

    if ! output=$("${cmd[@]}" 2>&1); then
        print_error "Git command failed: ${cmd[*]}" "Check git installation and repository state"
        return 1
    fi

    echo "$output"
    return 0
}

# JSON escape helper for output
json_escape() {
    local string="$1"
    string="${string//\\/\\\\}"
    string="${string//\"/\\\"}"
    string="${string//$'\n'/\\n}"
    echo "$string"
}

# Format output as JSON
output_json() {
    local status="$1"
    local message="$2"
    local data="${3:-{}}"

    local json_message=$(json_escape "$message")
    printf '{"status":"%s","message":"%s","data":%s}\n' "$status" "$json_message" "$data"
}

# Check if running in JSON mode
is_json_mode() {
    [[ "$JSON_MODE" == "true" ]]
}

# Initialize logging
setup_logging() {
    local log_dir="${1:-.specify/extensions/pre-implement/logs}"
    local log_file="$log_dir/run-$(date +%Y%m%d-%H%M%S).log"

    mkdir -p "$log_dir"

    # Redirect all output to log file and stdout
    exec 1> >(tee -a "$log_file")
    exec 2> >(tee -a "$log_file" >&2)

    echo "Pre-flight checks started at $(date)" >> "$log_file"
}

# Close logging
close_logging() {
    echo "Pre-flight checks completed at $(date)"
}

export -f print_check print_error prompt_user run_git_command json_escape output_json is_json_mode
