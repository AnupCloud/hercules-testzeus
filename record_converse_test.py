#!/usr/bin/env python3
"""
Optimized script to record Converse test execution with 2-minute limit
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

class ConverseTestRecorder:
    def __init__(self, project_dir="/Users/anup/Desktop/Anup/project/testzeus-hercules"):
        self.project_dir = Path(project_dir)
        self.input_file = "opt/input/converse_search.feature"
        self.output_dir = self.project_dir / "video-analysis-agent" / "converse_test_inputs"

    def setup_environment(self):
        """Set up environment variables for fast video recording"""
        print("Step 1: Configuring environment for FAST test execution...")
        os.environ['RECORD_VIDEO'] = 'true'
        os.environ['HEADLESS'] = 'false'
        os.environ['TAKE_SCREENSHOTS'] = 'false'
        os.environ['CAPTURE_NETWORK'] = 'false'
        os.environ['MAX_CHAT_ROUND'] = '3'
        os.environ['PAGE_LOAD_TIMEOUT'] = '10000'
        os.environ['ACTION_TIMEOUT'] = '8000'
        print("✓ Environment configured for fast execution")

    def cleanup_previous_runs(self):
        """Clean up previous test outputs"""
        print("\nStep 2: Cleaning up previous test outputs...")
        # Remove old converse test runs
        old_dirs = [
            self.project_dir / "opt/output" / "run_*",
            self.project_dir / "opt/log_files" / "Search_for_Chuck_70_on_Converse_India",
            self.project_dir / "opt/proofs" / "Search_for_Chuck_70_on_Converse_India",
            self.output_dir
        ]
        for pattern in old_dirs:
            try:
                if "*" in str(pattern):
                    import glob
                    for path in glob.glob(str(pattern)):
                        if Path(path).exists():
                            shutil.rmtree(path)
                elif pattern.exists():
                    shutil.rmtree(pattern)
            except:
                pass
        print("✓ Ready for new test run")

    def run_test(self):
        """Execute the Converse test with 2-minute timeout"""
        print("\nStep 3: Running Converse test with 2-minute timeout...")
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
            else:
                print("✓ Test completed successfully")

        except subprocess.TimeoutExpired:
            print("⚠ Test timed out after 2 minutes")
        except Exception as e:
            print(f"⚠ Error running test: {e}")

    def find_latest_run(self):
        """Find the most recent test run directory"""
        print("\nStep 4: Locating generated files...")

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
            "Search_for_Chuck_70_on_Converse_India" / latest_run / "agent_inner_thoughts.json"
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
            "converse_search.feature_result.xml"
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
            "Search_for_Chuck_70_on_Converse_India" / latest_run / "videos"
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

        if len(files_copied) == 3:
            print("\n✅ All files successfully recorded!")
            print("\nReady to run video-analysis-agent!")
        else:
            print(f"\n⚠ {len(files_copied)}/3 files collected")

        print("="*60)

    def record(self):
        """Main recording workflow"""
        print("\n" + "="*60)
        print("Converse Test Recording Script (2-minute limit)")
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
    recorder = ConverseTestRecorder()
    success = recorder.record()

    # Run video analysis if we have at least video + one other file
    if success:
        print("\n" + "="*60)
        print("Running Video Analysis Agent...")
        print("="*60 + "\n")

        import subprocess
        try:
            result = subprocess.run(
                [
                    "python", "main.py",
                    "--planning-log", "converse_test_inputs/planning_log.json",
                    "--video", "converse_test_inputs/video.webm",
                    "--test-output", "converse_test_inputs/test_result.xml",
                    "--output-dir", "converse_test_inputs/results"
                ],
                cwd=recorder.project_dir / "video-analysis-agent",
                timeout=300
            )

            if result.returncode == 0:
                print("\n✅ Video analysis completed!")
        except Exception as e:
            print(f"\n⚠ Video analysis error: {e}")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
