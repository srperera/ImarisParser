import os
import re
import sys
from datetime import datetime


def create_run_logfile(name, logfile_name, base_path="."):
    """
    Create a run directory named as 'run_YYYYMMDD_HHMMSS' inside base_path,
    and return the full path for the logfile inside that directory.

    Args:
        base_path (str): Base directory where the run folder will be created.
        logfile_name (str): Name of the log file to create inside the run folder.

    Returns:
        str: Full path to the log file.
    """
    # Create run directory name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir_name = f"run_{name}_{timestamp}"
    run_dir_path = os.path.join(base_path, run_dir_name)

    # Create the directory
    os.makedirs(run_dir_path, exist_ok=True)

    # Full path for the log file
    log_file_path = os.path.join(run_dir_path, logfile_name)

    return log_file_path


class Logger:
    """
    Simple logger that writes to both console and a log file.
    """

    def __init__(self, log_file):
        self.terminal = sys.stdout
        self.log = open(log_file, "a", encoding="utf-8")

    def write(self, message: str):
        # Write colored message to terminal
        self.terminal.write(message)
        self.terminal.flush()

        # Strip ANSI codes and write clean version to log file
        clean_message = self.remove_ansi_codes_keep_text(message)
        self.log.write(clean_message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def remove_ansi_codes_keep_text(self, text: str) -> str:
        """
        Removes only ANSI escape codes from a string, keeping the visible text.
        """
        # Match only ANSI escape sequences (\x1b[...m)
        ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
        return ansi_escape.sub("", text)

    def close(self):
        self.log.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        sys.stdout = self.terminal
