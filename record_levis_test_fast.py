#!/usr/bin/env python3
"""
Optimized script to record Levi's test execution with 2-minute limit
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

class LevisTestRecorderFast:
    def __init__(self, project_dir="/Users/anup/Desktop/Anup/project/testzeus-hercules"):
        self.project_dir = Path(project_dir)
        self.input_file = "opt/input/levis_search.feature"
        self.output_dir = self.project_dir / "video-analysis-agent" / "levis_test_inputs"

    def setup_environment(self):
        """Set up environment variables for fast video recording"""
        print("Step 1: Configuring environment for FAST test execution...")
        os.environ['RECORD_VIDEO'] = 'true'
        os.environ['HEADLESS'] = 'false'
        os.environ['TAKE_SCREENSHOTS'] = 'false'  # Disable screenshots for speed
        os.environ['CAPTURE_NETWORK'] = 'false'  # Disable network logs for speed
        os.environ['MAX_CHAT_ROUND'] = '3'  # Limit chat rounds
        os.environ['PAGE_LOAD_TIMEOUT'] = '10000'  # 10 seconds
        os.environ['ACTION_TIMEOUT'] = '5000'  # 5 seconds
        print("✓ Environment configured for fast execution")

    def cleanup_previous_runs(self):
        """Clean up previous test outputs"""
        print("\nStep 2: Cleaning up previous test outputs...")
        # Remove old test runs
        import glob
        old_runs = glob.glob(str(self.project_dir / "opt/output/run_*"))
        if old_runs:
            for run in old_runs[-3:]:  # Keep only last 3 runs
                try:
                    shutil.rmtree(run)
                    print(f"   Removed old run: {Path(run).name}")
                except:
                    pass
        print("✓ Ready for new test run")

    def run_test(self):
        """Execute the Levi's test with 2-minute timeout"""
        print("\nStep 3: Running Levi's test with 2-minute timeout...")
        print("This should complete in ~2 minutes...")

        cmd = [
            "poetry", "run", "python", "testzeus_hercules",
            "--input-file", self.input_file,
            "--output-path", "opt/output",
            "--test-data-path", "opt/test_data"
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if result.returncode != 0:
                print(f"⚠ Test completed with return code: {result.returncode}")
                # Continue anyway to collect whatever artifacts were generated
            else:
                print("✓ Test completed successfully")

        except subprocess.TimeoutExpired:
            print("⚠ Test timed out after 2 minutes (as expected)")
            # This is OK - we want to limit execution time
        except Exception as e:
            print(f"⚠ Error running test: {e}")

    def find_latest_run(self):
        """Find the most recent test run directory"""
        print("\nStep 4: Locating generated files...")

        # Find latest output run
        output_runs = sorted(
            (self.project_dir / "opt" / "output").glob("run_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if not output_runs:
            print("✗ No test runs found!")
            return None

        latest_run = output_runs[0].name
        print(f"✓ Latest run directory: {latest_run}")
        return latest_run

    def copy_files(self, latest_run):
        """Copy all required files to the video-analysis-agent input directory"""
        print("\nStep 5: Creating output directory...")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "results").mkdir(exist_ok=True)
        print(f"✓ Created: {self.output_dir}")

        print("\nStep 6: Copying files...")
        files_copied = []

        # Copy planning log
        planning_log_src = (
            self.project_dir / "opt" / "log_files" /
            "Search_for_white_round_tshirt_on_Levi's_India" / latest_run / "agent_inner_thoughts.json"
        )
        planning_log_dst = self.output_dir / "planning_log.json"

        if planning_log_src.exists():
            shutil.copy2(planning_log_src, planning_log_dst)
            print(f"✓ Copied planning_log.json ({planning_log_src.stat().st_size:,} bytes)")
            files_copied.append("planning_log.json")
        else:
            print(f"✗ Warning: Planning log not found at {planning_log_src}")

        # Copy test result XML
        test_result_src = (
            self.project_dir / "opt" / "output" / latest_run /
            "levis_search.feature_result.xml"
        )
        test_result_dst = self.output_dir / "test_result.xml"

        if test_result_src.exists():
            shutil.copy2(test_result_src, test_result_dst)
            print(f"✓ Copied test_result.xml ({test_result_src.stat().st_size:,} bytes)")
            files_copied.append("test_result.xml")
        else:
            print(f"✗ Warning: Test result not found at {test_result_src}")

        # Copy video
        video_dir = (
            self.project_dir / "opt" / "proofs" /
            "Search_for_white_round_tshirt_on_Levi's_India" / latest_run / "videos"
        )

        if video_dir.exists():
            video_files = list(video_dir.glob("*.webm")) + list(video_dir.glob("*.mp4"))
            if video_files:
                video_src = video_files[0]
                video_dst = self.output_dir / "video.webm"
                shutil.copy2(video_src, video_dst)
                size_mb = video_src.stat().st_size / (1024 * 1024)
                print(f"✓ Copied video.webm ({size_mb:.2f} MB)")
                files_copied.append("video.webm")
            else:
                print(f"✗ Warning: No video files found in {video_dir}")
        else:
            print(f"✗ Warning: Video directory not found at {video_dir}")

        return files_copied

    def display_summary(self, files_copied):
        """Display summary of what was recorded"""
        print("\n" + "="*60)
        print("Recording Complete!")
        print("="*60)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"\nFiles created ({len(files_copied)}/3):")

        if self.output_dir.exists():
            for item in sorted(self.output_dir.iterdir()):
                if item.is_file():
                    size = item.stat().st_size
                    size_str = f"{size:,} bytes" if size < 1024*1024 else f"{size/(1024*1024):.2f} MB"
                    print(f"  ✓ {item.name} ({size_str})")

        if len(files_copied) >= 2:  # At least video and one other file
            print("\n✅ Test artifacts collected!")
            print("\nYou can now run the video-analysis-agent with:")
            print("\n  cd video-analysis-agent")
            print("  python main.py \\")
            print("    --planning-log levis_test_inputs/planning_log.json \\")
            print("    --video levis_test_inputs/video.webm \\")
            print("    --test-output levis_test_inputs/test_result.xml \\")
            print("    --output-dir levis_test_inputs/results")
        else:
            print(f"\n⚠ Warning: Only {len(files_copied)}/3 files were recorded")
            print("   Some files may be missing. Check the warnings above.")

        print("="*60)

    def record(self):
        """Main recording workflow"""
        print("\n" + "="*60)
        print("Levi's Fast Test Recording Script (2-minute limit)")
        print("="*60 + "\n")

        self.setup_environment()
        self.cleanup_previous_runs()
        self.run_test()

        latest_run = self.find_latest_run()
        if not latest_run:
            print("\n❌ Failed to find test run. Exiting.")
            sys.exit(1)

        files_copied = self.copy_files(latest_run)
        self.display_summary(files_copied)

        return len(files_copied) >= 2

def main():
    recorder = LevisTestRecorderFast()
    success = recorder.record()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
