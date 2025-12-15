#!/bin/bash
# Test runner script for Contextinator

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Contextinator Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"

# Parse arguments
COVERAGE=false
HTML=false
UNIT_ONLY=false
INTEGRATION_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage)
            COVERAGE=true
            shift
            ;;
        --html)
            HTML=true
            COVERAGE=true
            shift
            ;;
        --unit)
            UNIT_ONLY=true
            shift
            ;;
        --integration)
            INTEGRATION_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--coverage] [--html] [--unit] [--integration]"
            exit 1
            ;;
    esac
done

# Build pytest command
CMD="pytest"

if [ "$COVERAGE" = true ]; then
    CMD="$CMD --cov=src/contextinator --cov-report=term"
fi

if [ "$HTML" = true ]; then
    CMD="$CMD --cov-report=html"
fi

if [ "$UNIT_ONLY" = true ]; then
    CMD="$CMD tests/ -m 'not integration'"
elif [ "$INTEGRATION_ONLY" = true ]; then
    CMD="$CMD tests/integration/ -m integration"
else
    CMD="$CMD tests/"
fi

# Run tests
echo -e "\n${BLUE}Running command: $CMD${NC}\n"
eval $CMD

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}\n"
    
    if [ "$HTML" = true ]; then
        echo -e "${BLUE}Coverage report: htmlcov/index.html${NC}\n"
    fi
else
    echo -e "\n${RED}✗ Tests failed with exit code $EXIT_CODE${NC}\n"
fi

exit $EXIT_CODE
