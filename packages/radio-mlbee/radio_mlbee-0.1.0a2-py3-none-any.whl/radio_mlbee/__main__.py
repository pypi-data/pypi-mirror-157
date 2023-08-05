"""Run app.py from __main__.py."""
# pylint: disable=no-value-for-parameter
import subprocess
import sys

from pathlib import Path

app = Path(__file__).with_name("app.py")
assert app.is_file, f"{app} does not exist or is not a file."

print(sys.executable, app.as_posix())
# /root/.cache/pypoetry/virtualenvs/radio-mlbee-VA82Wl8V-py3.8/bin/python /usr/src/app/radio_mlbee/app.py

subprocess.call(
    [sys.executable, app.as_posix()],
    text=True,
    # shell=True,
)
