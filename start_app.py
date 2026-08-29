import subprocess
import sys

subprocess.Popen(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py"
    ],
    creationflags=subprocess.CREATE_NEW_CONSOLE
)