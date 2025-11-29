#!/usr/bin/env bash

#################################################################
# Video Analysis Agent - Automated Validation Script
#
# This script validates that the agent is working correctly by:
# 1. Checking all dependencies are installed
# 2. Running the agent on sample inputs
# 3. Verifying output files are generated
# 4. Checking report content for expected structure
#################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_test() {
    echo -e "\n${YELLOW}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}✓ PASS${NC} $1"
    ((TESTS_PASSED++))
}

print_fail() {
    echo -e "${RED}✗ FAIL${NC} $1"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${BLUE}ℹ INFO${NC} $1"
}

# Change to script directory
cd "$(dirname "$0")"

print_header "Video Analysis Agent - Validation Suite"

#################################################################
# Test 1: Check Python version
#################################################################
print_test "Checking Python version (≥3.10)"
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
    print_pass "Python $PYTHON_VERSION detected"
else
    print_fail "Python $PYTHON_VERSION is too old (need ≥3.10)"
fi

#################################################################
# Test 2: Check virtual environment
#################################################################
print_test "Checking virtual environment"
if [ -d ".venv" ]; then
    print_pass "Virtual environment exists at .venv/"
else
    print_fail "Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

#################################################################
# Test 3: Check required dependencies
#################################################################
print_test "Checking required Python packages"

REQUIRED_PACKAGES=("cv2" "langgraph" "langchain" "xml.etree.ElementTree")
ALL_DEPS_OK=true

for package in "${REQUIRED_PACKAGES[@]}"; do
    if .venv/bin/python -c "import $package" 2>/dev/null; then
        print_info "  ✓ $package installed"
    else
        print_fail "  ✗ $package missing"
        ALL_DEPS_OK=false
    fi
done

if $ALL_DEPS_OK; then
    print_pass "All required packages installed"
else
    print_fail "Some packages missing. Run: pip install -r requirements.txt"
fi

#################################################################
# Test 4: Check source files exist
#################################################################
print_test "Checking source code structure"

SOURCE_FILES=(
    "main.py"
    "src/planning_log_parser.py"
    "src/video_analyzer.py"
    "src/output_comparator.py"
    "src/deviation_reporter.py"
)

ALL_FILES_OK=true
for file in "${SOURCE_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_info "  ✓ $file exists"
    else
        print_fail "  ✗ $file missing"
        ALL_FILES_OK=false
    fi
done

if $ALL_FILES_OK; then
    print_pass "All source files present"
else
    print_fail "Some source files missing"
fi

#################################################################
# Test 5: Check sample input files
#################################################################
print_test "Checking sample input files"

SAMPLE_INPUTS=(
    "sample_inputs/agent_inner_logs.json"
    "sample_inputs/video.webm"
    "sample_inputs/test_result.xml"
)

ALL_INPUTS_OK=true
for file in "${SAMPLE_INPUTS[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(du -h "$file" | cut -f1)
        print_info "  ✓ $file ($SIZE)"
    else
        print_fail "  ✗ $file missing"
        ALL_INPUTS_OK=false
    fi
done

if $ALL_INPUTS_OK; then
    print_pass "All sample inputs present"
else
    print_fail "Some sample inputs missing"
fi

#################################################################
# Test 6: Run agent on sample data
#################################################################
print_test "Running agent on sample data"

# Clean output directory
rm -rf test_output
mkdir -p test_output

# Run the agent
if .venv/bin/python main.py \
    --planning-log sample_inputs/agent_inner_logs.json \
    --video sample_inputs/video.webm \
    --test-output sample_inputs/test_result.xml \
    --output-dir test_output \
    > test_output/run.log 2>&1; then
    print_pass "Agent executed successfully"
else
    print_fail "Agent execution failed. Check test_output/run.log"
    cat test_output/run.log
fi

#################################################################
# Test 7: Verify output files generated
#################################################################
print_test "Verifying output files"

OUTPUT_FILES=(
    "test_output/deviation_report.json"
    "test_output/deviation_report.md"
)

ALL_OUTPUTS_OK=true
for file in "${OUTPUT_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(du -h "$file" | cut -f1)
        print_info "  ✓ $file generated ($SIZE)"
    else
        print_fail "  ✗ $file not generated"
        ALL_OUTPUTS_OK=false
    fi
done

if $ALL_OUTPUTS_OK; then
    print_pass "All output files generated"
else
    print_fail "Some output files missing"
fi

#################################################################
# Test 8: Validate JSON report structure
#################################################################
print_test "Validating JSON report structure"

if [ -f "test_output/deviation_report.json" ]; then
    # Check required fields exist
    HAS_SUMMARY=$(cat test_output/deviation_report.json | grep -q '"summary"' && echo "yes" || echo "no")
    HAS_STEPS=$(cat test_output/deviation_report.json | grep -q '"steps"' && echo "yes" || echo "no")
    HAS_TEST_RESULT=$(cat test_output/deviation_report.json | grep -q '"test_result"' && echo "yes" || echo "no")

    if [ "$HAS_SUMMARY" = "yes" ] && [ "$HAS_STEPS" = "yes" ] && [ "$HAS_TEST_RESULT" = "yes" ]; then
        print_pass "JSON report has correct structure"

        # Extract summary info
        TOTAL=$(cat test_output/deviation_report.json | grep -o '"total_steps": [0-9]*' | grep -o '[0-9]*')
        OBSERVED=$(cat test_output/deviation_report.json | grep -o '"observed_steps": [0-9]*' | grep -o '[0-9]*')
        DEVIATIONS=$(cat test_output/deviation_report.json | grep -o '"deviation_count": [0-9]*' | grep -o '[0-9]*')

        print_info "  Total steps: $TOTAL"
        print_info "  Observed: $OBSERVED"
        print_info "  Deviations: $DEVIATIONS"
    else
        print_fail "JSON report missing required fields"
    fi
else
    print_fail "JSON report not found"
fi

#################################################################
# Test 9: Validate Markdown report format
#################################################################
print_test "Validating Markdown report format"

if [ -f "test_output/deviation_report.md" ]; then
    # Check for key sections
    HAS_HEADER=$(grep -q "# Test Execution Deviation Report" test_output/deviation_report.md && echo "yes" || echo "no")
    HAS_SUMMARY=$(grep -q "## Summary" test_output/deviation_report.md && echo "yes" || echo "no")
    HAS_TABLE=$(grep -q "| Step | Description |" test_output/deviation_report.md && echo "yes" || echo "no")
    HAS_CONFIDENCE=$(grep -q "Confidence" test_output/deviation_report.md && echo "yes" || echo "no")

    if [ "$HAS_HEADER" = "yes" ] && [ "$HAS_SUMMARY" = "yes" ] && [ "$HAS_TABLE" = "yes" ] && [ "$HAS_CONFIDENCE" = "yes" ]; then
        print_pass "Markdown report has correct format"
    else
        print_fail "Markdown report missing required sections"
        [ "$HAS_HEADER" = "no" ] && print_info "  ✗ Missing header"
        [ "$HAS_SUMMARY" = "no" ] && print_info "  ✗ Missing summary"
        [ "$HAS_TABLE" = "no" ] && print_info "  ✗ Missing results table"
        [ "$HAS_CONFIDENCE" = "no" ] && print_info "  ✗ Missing confidence scores"
    fi
else
    print_fail "Markdown report not found"
fi

#################################################################
# Test 10: Check documentation files
#################################################################
print_test "Checking documentation completeness"

DOC_FILES=(
    "README.md"
    "QUICKSTART.md"
    "VIDEO_SCRIPT.md"
    "DEVIATION_EXAMPLES.md"
)

ALL_DOCS_OK=true
for file in "${DOC_FILES[@]}"; do
    if [ -f "$file" ]; then
        LINES=$(wc -l < "$file")
        print_info "  ✓ $file ($LINES lines)"
    else
        print_fail "  ✗ $file missing"
        ALL_DOCS_OK=false
    fi
done

if $ALL_DOCS_OK; then
    print_pass "All documentation files present"
else
    print_fail "Some documentation missing"
fi

#################################################################
# Test 11: Puma test validation (if available)
#################################################################
print_test "Checking Puma test inputs"

if [ -f "puma_test_inputs/planning_log.json" ] && \
   [ -f "puma_test_inputs/video.webm" ] && \
   [ -f "puma_test_inputs/test_result.xml" ]; then
    print_pass "Puma test inputs available"

    # Run on Puma data
    print_info "  Running agent on Puma test..."
    if .venv/bin/python main.py \
        --planning-log puma_test_inputs/planning_log.json \
        --video puma_test_inputs/video.webm \
        --test-output puma_test_inputs/test_result.xml \
        --output-dir test_output/puma \
        > test_output/puma_run.log 2>&1; then
        print_pass "Puma test analysis completed"

        if [ -f "test_output/puma/deviation_report.json" ]; then
            PUMA_DEVIATIONS=$(cat test_output/puma/deviation_report.json | grep -o '"deviation_count": [0-9]*' | grep -o '[0-9]*')
            print_info "  Puma test deviations: $PUMA_DEVIATIONS"
        fi
    else
        print_fail "Puma test analysis failed"
    fi
else
    print_info "Puma test inputs not available (optional)"
fi

#################################################################
# Summary
#################################################################
print_header "Validation Summary"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
echo ""
echo -e "${GREEN}Passed: $TESTS_PASSED${NC} / $TOTAL_TESTS"
echo -e "${RED}Failed: $TESTS_FAILED${NC} / $TOTAL_TESTS"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}   ✨ ALL TESTS PASSED! Agent is working correctly.${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}   ⚠️  SOME TESTS FAILED! Please review errors above.${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi
