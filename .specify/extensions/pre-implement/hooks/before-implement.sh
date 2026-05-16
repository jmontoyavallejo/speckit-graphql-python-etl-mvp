#!/usr/bin/env bash
# Hook entry point for speckit-implement pre-flight checks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" && pwd)"
PRE_FLIGHT_SCRIPT="$SCRIPT_DIR/pre-flight-checks.sh"

# Check if pre-flight script exists
if [[ ! -f "$PRE_FLIGHT_SCRIPT" ]]; then
    echo "ERROR: Pre-flight checks script not found at $PRE_FLIGHT_SCRIPT" >&2
    exit 1
fi

# Get feature directory from environment or arguments
FEATURE_DIR="${SPECIFY_FEATURE_DIRECTORY:-.}"

# Run pre-flight checks
# Pass through all arguments and add feature directory
bash "$PRE_FLIGHT_SCRIPT" --feature-dir "$FEATURE_DIR" "$@"
exit_code=$?

exit $exit_code
