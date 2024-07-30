import sys

sys_platform = "win" if sys.platform.startswith("win") else sys.platform

venv_bin_dir = "bin"
bin_ext = ""

if sys_platform == "win":
    venv_bin_dir = "Scripts"
    bin_ext = ".exe"
