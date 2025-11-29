#!/bin/bash
# Script to record Puma test execution with all necessary artifacts for video-analysis-agent

set -e  # Exit on error

echo "========================================="
echo "Puma Test Recording Script"
echo "========================================="

# Configuration
PROJECT_DIR="/Users/anup/Desktop/Anup/project/testzeus-hercules"
INPUT_FILE="opt/input/puma_search.feature"
OUTPUT_DIR="video-analysis-agent/puma_test_inputs"

# Step 1: Enable video recording temporarily
echo "Step 1: Configuring environment for video recording..."
export RECORD_VIDEO=true
export HEADLESS=false
export TAKE_SCREENSHOTS=true
export CAPTURE_NETWORK=true

# Step 2: Clean up previous output
echo "Step 2: Cleaning up previous test outputs..."
rm -rf opt/output/run_*
rm -rf opt/log_files/Search_for_Palermo_on_Puma_India/*
rm -rf opt/proofs/Search_for_Palermo_on_Puma_India/*

# Step 3: Run the test
echo "Step 3: Running Puma test with video recording..."
poetry run python testzeus_hercules \
  --input-file "$INPUT_FILE" \
  --output-path opt/output \
  --test-data-path opt/test_data

# Step 4: Find the latest run directory
echo "Step 4: Locating generated files..."
LATEST_RUN=$(ls -t opt/output/ | head -1)
echo "Latest run directory: $LATEST_RUN"

# Step 5: Create output directory
echo "Step 5: Creating output directory structure..."
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/results"

# Step 6: Copy files to the video-analysis-agent input directory
echo "Step 6: Copying files..."

# Copy planning log (agent_inner_thoughts.json)
if [ -f "opt/log_files/Search_for_Palermo_on_Puma_India/$LATEST_RUN/agent_inner_thoughts.json" ]; then
  cp "opt/log_files/Search_for_Palermo_on_Puma_India/$LATEST_RUN/agent_inner_thoughts.json" \
     "$OUTPUT_DIR/planning_log.json"
  echo "✓ Copied planning_log.json"
else
  echo "✗ Warning: agent_inner_thoughts.json not found"
fi

# Copy test result XML
if [ -f "opt/output/$LATEST_RUN/puma_search.feature_result.xml" ]; then
  cp "opt/output/$LATEST_RUN/puma_search.feature_result.xml" \
     "$OUTPUT_DIR/test_result.xml"
  echo "✓ Copied test_result.xml"
else
  echo "✗ Warning: test_result.xml not found"
fi

# Copy video
VIDEO_DIR="opt/proofs/Search_for_Palermo_on_Puma_India/$LATEST_RUN/videos"
if [ -d "$VIDEO_DIR" ] && [ "$(ls -A $VIDEO_DIR)" ]; then
  VIDEO_FILE=$(find "$VIDEO_DIR" -name "*.webm" -o -name "*.mp4" | head -1)
  if [ -n "$VIDEO_FILE" ]; then
    cp "$VIDEO_FILE" "$OUTPUT_DIR/video.webm"
    echo "✓ Copied video file"
  else
    echo "✗ Warning: No video file found in $VIDEO_DIR"
  fi
else
  echo "✗ Warning: Video directory not found or empty"
fi

# Step 7: Display summary
echo ""
echo "========================================="
echo "Recording Complete!"
echo "========================================="
echo "Output directory: $OUTPUT_DIR"
echo ""
echo "Files created:"
ls -lh "$OUTPUT_DIR"
echo ""
echo "You can now run the video-analysis-agent with:"
echo "cd video-analysis-agent"
echo "python main.py \\"
echo "  --planning-log puma_test_inputs/planning_log.json \\"
echo "  --video puma_test_inputs/video.webm \\"
echo "  --test-output puma_test_inputs/test_result.xml \\"
echo "  --output-dir puma_test_inputs/results"
echo "========================================="
