from pathlib import Path
import subprocess
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_app():
  """Entry point for the application when used as a package."""
  try:
    stl_path = Path(__file__).parent / "tof_stl.py"

    # Use subprocess to run streamlit properly
    cmd = [sys.executable, "-m", "streamlit", "run", str(stl_path)]
    subprocess.run(cmd)

  except Exception as e:
    logger.error(f"Failed to launch application: {e}")
    sys.exit(1)


if __name__ == "__main__":
  run_app()
