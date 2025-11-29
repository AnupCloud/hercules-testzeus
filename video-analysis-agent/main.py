"""
Video Analysis Agent - Main Entry Point

This agent evaluates whether a Hercules test run was executed as planned by comparing:
1. The agent's planning log (thoughts/steps)
2. The video evidence of the run
3. The final test output
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

from src.planning_log_parser import PlanningLogParser
from src.video_analyzer import VideoAnalyzer
from src.output_comparator import OutputComparator
from src.deviation_reporter import DeviationReporter


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def main():
    parser = argparse.ArgumentParser(
        description='Video Analysis Agent - Validate Hercules test execution'
    )
    parser.add_argument(
        '--planning-log',
        type=str,
        required=True,
        help='Path to the planning log JSON file'
    )
    parser.add_argument(
        '--video',
        type=str,
        required=True,
        help='Path to the video file or directory containing videos'
    )
    parser.add_argument(
        '--test-output',
        type=str,
        required=True,
        help='Path to the test output (XML/HTML)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Directory to save the deviation report'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(Path(args.config))
    
    # Initialize components
    print("🚀 Starting Video Analysis Agent...")
    
    # Step 1: Parse Planning Log
    print(f"\\n📋 Step 1: Parsing planning log from {args.planning_log}")
    log_parser = PlanningLogParser(args.planning_log)
    planned_steps = log_parser.extract_steps()
    print(f"   Found {len(planned_steps)} planned steps")
    
    # Step 2: Analyze Video(s)
    print(f"\\n🎥 Step 2: Analyzing video(s) from {args.video}")
    video_analyzer = VideoAnalyzer(args.video, config=config)
    video_analysis = video_analyzer.analyze()
    print(f"   Processed {video_analysis['video_count']} video(s)")
    
    #Step 3: Compare with Final Output
    print(f"\\n📄 Step 3: Cross-checking with test output from {args.test_output}")
    comparator = OutputComparator(args.test_output)
    test_result = comparator.get_result()
    print(f"   Test Status: {test_result['status']}")
    
    # Step 4: Generate Deviation Report
    print(f"\\n🔍 Step 4: Generating deviation report...")
    reporter = DeviationReporter(
        planned_steps=planned_steps,
        video_analysis=video_analysis,
        test_result=test_result
    )
    report = reporter.generate_report()
    
    # Save report
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = output_dir / 'deviation_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Also save as markdown
    md_report_path = output_dir / 'deviation_report.md'
    with open(md_report_path, 'w') as f:
        f.write(reporter.format_markdown())
    
    print(f"\\n✅ Report generated successfully!")
    print(f"   JSON: {report_path}")
    print(f"   Markdown: {md_report_path}")
    
    # Print summary
    print(f"\\n📊 Summary:")
    print(f"   Total Steps: {report['summary']['total_steps']}")
    print(f"   Observed: {report['summary']['observed_steps']}")
    print(f"   Deviations: {report['summary']['deviation_count']}")
    
    if report['summary']['deviation_count'] == 0:
        print(f"\\n   ✨ No deviations detected!")
    else:
        print(f"\\n   ⚠️  {report['summary']['deviation_count']} deviation(s) found")
    
    # Return exit code
    return 0 if report['summary']['deviation_count'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
