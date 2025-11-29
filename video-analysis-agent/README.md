# Video Analysis Agent

An intelligent LangGraph-based agent that validates Hercules test execution by analyzing planning logs, video recordings, and test outputs to detect deviations from the intended test plan.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Output](#output)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## Overview

This agent evaluates whether a Hercules test run was executed as planned by cross-referencing three key artifacts:

1. **Planning Log** - The agent's internal thought process and planned steps
2. **Video Recording** - Visual evidence of the actual test execution
3. **Test Output** - The final test result (XML/HTML format)

By comparing these artifacts, the agent identifies deviations where the executed test differs from the planned behavior.

## Features

- **LangGraph-Powered Workflow**: Orchestrates multi-step analysis with state management and conditional routing
- **Video Analysis**: Uses OpenCV to detect scene changes, UI transitions, and visual events
- **LLM Integration**: Leverages Claude for intelligent step interpretation and matching
- **Dual Output Formats**: Generates both JSON (machine-readable) and Markdown (human-readable) reports
- **Multi-Video Support**: Can analyze multiple video files from a test run
- **Configurable**: Flexible configuration for video analysis parameters and LLM settings
- **Detailed Reporting**: Provides confidence scores and evidence for each detection

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT ARTIFACTS                       │
├────────────────┬──────────────────┬─────────────────────┤
│ Planning Log   │ Video Recording  │ Test Output         │
│ (JSON)         │ (WebM/MP4)       │ (XML/HTML)          │
└────────┬───────┴─────────┬────────┴──────────┬──────────┘
         │                 │                    │
         ▼                 ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌────────────────┐
│ Planning Log    │ │ Video Analyzer  │ │ Output         │
│ Parser          │ │                 │ │ Comparator     │
│                 │ │ - OpenCV        │ │                │
│ - Extract steps │ │ - Scene detect  │ │ - Parse XML    │
│ - Classify type │ │ - Event track   │ │ - Get status   │
└────────┬────────┘ └────────┬────────┘ └────────┬───────┘
         │                   │                    │
         └───────────────────┼────────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │ LangGraph Orchestration  │
              │                          │
              │ • Initialize State       │
              │ • Analyze Each Step      │
              │ • Match with Video       │
              │ • Detect Deviations      │
              │ • Generate Report        │
              └──────────────┬───────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │ Deviation Reporter       │
              │                          │
              │ • JSON Report            │
              │ • Markdown Report        │
              └──────────────────────────┘
```

### Analysis Workflow

1. **Parse Planning Log**: Extracts intended steps from the agent's planning log
2. **Analyze Video**: Processes video frames to detect visual events and scene changes
3. **Compare Output**: Validates against the final test result
4. **Generate Report**: Creates detailed deviation reports with confidence scores

## Prerequisites

- **Python**: 3.10 or higher
- **uv**: Modern Python package manager (will be installed automatically by setup script)
- **Anthropic API Key**: Required for LLM-based step interpretation

## Installation

### Quick Setup (Recommended)

The fastest way to get started:

```bash
# Clone the repository (if needed)
git clone <your-repo-url>
cd video-analysis-agent

# Run the setup script (installs uv if needed and sets up environment)
chmod +x setup.sh
./setup.sh
```

### Manual Setup with uv

If you prefer manual control:

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create virtual environment
uv venv

# 3. Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# 4. Install dependencies
uv pip install -e .
```

### Traditional pip Installation

If you prefer using pip:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or add it to your `config.json` file (see below).

### Configuration File

Create or modify `config.json` in the project root:

```json
{
  "frame_skip": 30,
  "anthropic_api_key": "your-api-key-here",
  "confidence_threshold": 0.7,
  "video_analysis": {
    "scene_change_threshold": 30,
    "max_events_per_step": 5
  },
  "llm_config": {
    "model": "claude-3-haiku-20240307",
    "temperature": 0,
    "max_tokens": 500
  }
}
```

**Configuration Options:**

- `frame_skip`: Number of frames to skip during video analysis (higher = faster but less precise)
- `anthropic_api_key`: Your Anthropic API key for Claude access
- `confidence_threshold`: Minimum confidence score for deviation detection (0.0-1.0)
- `video_analysis.scene_change_threshold`: Sensitivity for scene change detection
- `video_analysis.max_events_per_step`: Maximum events to extract per step
- `llm_config.model`: Claude model to use (haiku for speed, sonnet for accuracy)
- `llm_config.temperature`: LLM temperature (0 for deterministic, higher for creative)
- `llm_config.max_tokens`: Maximum tokens per LLM response

## Usage

### Basic Usage

Analyze a test run with the minimum required inputs:

```bash
# Activate virtual environment (if not already activated)
source .venv/bin/activate

# Run the agent
python main.py \
  --planning-log sample_inputs/agent_inner_logs.json \
  --video sample_inputs/video.webm \
  --test-output sample_inputs/test_result.xml
```

### With Custom Output Directory

Specify where to save the reports:

```bash
python main.py \
  --planning-log sample_inputs/agent_inner_logs.json \
  --video sample_inputs/video.webm \
  --test-output sample_inputs/test_result.xml \
  --output-dir my_results
```

### With Custom Configuration

Use a custom configuration file:

```bash
python main.py \
  --planning-log sample_inputs/agent_inner_logs.json \
  --video sample_inputs/video.webm \
  --test-output sample_inputs/test_result.xml \
  --config my_config.json
```

### Analyzing Multiple Videos

If your test run produced multiple video files, provide a directory:

```bash
python main.py \
  --planning-log sample_inputs/agent_inner_logs.json \
  --video sample_inputs/videos/ \
  --test-output sample_inputs/test_result.xml
```

### Example with Sample Data

The project includes sample inputs for testing:

```bash
python main.py \
  --planning-log sample_inputs/agent_inner_logs.json \
  --video sample_inputs/video.webm \
  --test-output sample_inputs/test_result.xml \
  --output-dir output
```

## Project Structure

```
video-analysis-agent/
├── main.py                      # Entry point for the agent
├── src/                         # Source code
│   ├── __init__.py
│   ├── planning_log_parser.py  # Extract steps from planning logs
│   ├── video_analyzer.py       # Analyze video recordings with OpenCV
│   ├── output_comparator.py    # Parse and validate test outputs
│   └── deviation_reporter.py   # LangGraph workflow & report generation
├── sample_inputs/               # Example input files
│   ├── agent_inner_logs.json   # Sample planning log
│   ├── video.webm              # Sample video recording
│   ├── test_result.xml         # Sample test result (XML)
│   ├── test_result.html        # Sample test result (HTML)
│   └── wrangler_*.{json,xml,webm}  # Additional examples
├── tests/                       # Unit tests
├── config.json                  # Configuration file
├── pyproject.toml              # Project metadata and dependencies
├── requirements.txt            # Python dependencies (for pip)
├── setup.sh                    # Quick setup script
├── validate.sh                 # Validation script
├── .gitignore                  # Git ignore patterns
└── README.md                   # This file
```

## Output

The agent generates two report formats in the specified output directory:

### 1. JSON Report (`deviation_report.json`)

Machine-readable format for automation and CI/CD integration:

```json
{
  "summary": {
    "total_steps": 10,
    "observed_steps": 8,
    "deviation_count": 2,
    "status": "2 deviation(s) found"
  },
  "steps": [
    {
      "step_number": 1,
      "description": "Navigate to https://example.com",
      "observed": true,
      "confidence": 0.95,
      "evidence": "Scene change detected at 00:02.3",
      "deviation": false
    },
    {
      "step_number": 4,
      "description": "Click 'Filter' button",
      "observed": false,
      "confidence": 0.85,
      "evidence": "No matching visual event found",
      "deviation": true
    }
  ],
  "metadata": {
    "analysis_timestamp": "2024-01-15T10:30:00Z",
    "video_duration": "00:02:45",
    "total_events": 15
  }
}
```

### 2. Markdown Report (`deviation_report.md`)

Human-readable format for review:

```markdown
# Deviation Report

## Summary
- **Total Steps**: 10
- **Observed Steps**: 8
- **Deviations Found**: 2
- **Status**: 2 deviation(s) found

## Detailed Analysis

| Step | Description | Result | Confidence | Evidence |
|------|-------------|--------|------------|----------|
| 1 | Navigate to https://example.com | ✅ Observed | 95% | Scene change at 00:02.3 |
| 2 | Click Search icon | ✅ Observed | 92% | UI interaction detected |
| 3 | Enter "Rainbow sweater" | ✅ Observed | 88% | Text input event |
| 4 | Click 'Filter' button | ❌ Deviation | 85% | No matching event |
```

### Output Location

By default, reports are saved to the `output/` directory. You can customize this with the `--output-dir` flag.

## Advanced Usage

### Custom Video Analysis Parameters

Adjust video analysis sensitivity in `config.json`:

```json
{
  "frame_skip": 15,  // Process every 15th frame (lower = more precise)
  "video_analysis": {
    "scene_change_threshold": 25,  // Lower = more sensitive
    "max_events_per_step": 10      // Capture more events
  }
}
```

### Using Different Claude Models

Switch between Claude models for different speed/accuracy tradeoffs:

```json
{
  "llm_config": {
    "model": "claude-3-sonnet-20240229",  // More accurate
    "temperature": 0.3,
    "max_tokens": 1000
  }
}
```

**Model Recommendations:**
- `claude-3-haiku-20240307`: Fast and cost-effective for most cases
- `claude-3-sonnet-20240229`: Better accuracy for complex test scenarios
- `claude-3-opus-20240229`: Highest accuracy (slower and more expensive)

### Environment Variable Configuration

Instead of storing the API key in `config.json`, use environment variables:

```bash
export ANTHROPIC_API_KEY="your-api-key"
export FRAME_SKIP=30
export CONFIDENCE_THRESHOLD=0.7

python main.py \
  --planning-log sample_inputs/agent_inner_logs.json \
  --video sample_inputs/video.webm \
  --test-output sample_inputs/test_result.xml
```

## Troubleshooting

### Common Issues

#### Issue: "uv: command not found"

**Solution**: Install uv manually:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Then restart your shell or run:
source ~/.bashrc  # or ~/.zshrc
```

#### Issue: "No module named 'cv2'"

**Solution**: Ensure OpenCV is installed:
```bash
uv pip install opencv-python
```

#### Issue: "Anthropic API key not found"

**Solution**: Set your API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```
Or add it to `config.json`.

#### Issue: "Video analysis taking too long"

**Solution**: Increase `frame_skip` in `config.json`:
```json
{
  "frame_skip": 60  // Process every 60th frame
}
```

#### Issue: "Too many false deviations detected"

**Solution**: Lower the `confidence_threshold`:
```json
{
  "confidence_threshold": 0.6  // Lower threshold
}
```

### Debug Mode

For detailed debugging output, you can modify the logging level in the source code or add verbose flags (if implemented).

## Development

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run tests
pytest tests/
```

### Code Formatting

The project uses `black` and `ruff` for code formatting:

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Format code
black .

# Lint code
ruff check .
```

### Adding New Features

The modular architecture makes it easy to extend:

1. **New Analyzers**: Add to `src/` directory
2. **LangGraph Nodes**: Modify `src/deviation_reporter.py`
3. **Output Formats**: Extend the `DeviationReporter` class

### Project Dependencies

Main dependencies (see `pyproject.toml` for complete list):

- `langgraph>=0.2.0` - Workflow orchestration
- `langchain>=0.3.0` - LLM framework
- `langchain-anthropic>=0.3.0` - Claude integration
- `opencv-python>=4.8.0` - Video analysis
- `numpy>=1.24.0` - Numerical operations
- `beautifulsoup4>=4.12.0` - HTML parsing
- `lxml>=4.9.0` - XML parsing

## Why uv?

This project uses [uv](https://github.com/astral-sh/uv) as the recommended package manager because:

- **Fast**: 10-100x faster than pip for dependency resolution
- **Reliable**: Consistent dependency resolution across environments
- **Modern**: Built with Rust for performance and reliability
- **Compatible**: Works with standard `pyproject.toml` and `requirements.txt`
- **Easy**: Simple installation and usage

## License

MIT

## Contributing

This project was built as part of the TestZeus hiring assignment. Contributions and feedback are welcome!

## References

- [TestZeus Hercules](https://github.com/test-zeus-ai/testzeus-hercules) - The test automation framework
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) - Graph-based LLM workflows
- [OpenCV Documentation](https://docs.opencv.org/) - Computer vision library
- [Anthropic Claude](https://www.anthropic.com/claude) - LLM provider
- [uv Documentation](https://github.com/astral-sh/uv) - Fast Python package manager
