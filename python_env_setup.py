#!/usr/bin/env python3
"""Interactive helper to install a newer Python with pyenv and pyenv-virtualenv.

Supported environments
- macOS
- Ubuntu (including Ubuntu running under WSL)

On Windows, this script prints instructions for enabling WSL and installing Ubuntu,
then you should run this script *inside* the Ubuntu / WSL environment.

The script will:
1. Detect your OS / environment.
2. Offer to install pyenv (and optionally pyenv-virtualenv).
3. Show you a list of recent CPython versions you can pick from.
4. Install the selected version with pyenv.
5. Optionally set it as your global default Python.
6. Create a demo project folder in your home directory using pyenv-virtualenv.
"""

import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
from typing import List, Optional


# Enforce a minimum Python version at runtime for clarity.
# Note: the script uses f-strings and other Python 3.6+ features, so it will
# only run on Python 3.6 or newer.
if sys.version_info < (3, 6):
    sys.stderr.write(
        "This script requires Python 3.6 or newer. "
        "Detected Python {}.{}\n".format(sys.version_info[0], sys.version_info[1])
    )
    raise SystemExit(1)


# ------------------------ helpers ------------------------


def print_banner() -> None:
    print("=" * 72)
    print(" Python version & pyenv-virtualenv setup helper")
    print("=" * 72)
    print()


def run_cmd(
    cmd,
    *,
    check: bool = True,
    capture_output: bool = False,
    text: bool = True,
    shell: bool = False,
    env: Optional[dict] = None,
    cwd: Optional[str] = None,
):
    """Wrapper around subprocess.run with basic error handling."""

    if capture_output:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=True,
            text=text,
            shell=shell,
            env=env,
            cwd=cwd,
        )
        return result.stdout
    else:
        return subprocess.run(
            cmd,
            check=check,
            shell=shell,
            env=env,
            cwd=cwd,
        )


def ask_yes_no(prompt: str, default: Optional[bool] = True) -> bool:
    if default is True:
        suffix = " [Y/n]: "
    elif default is False:
        suffix = " [y/N]: "
    else:
        suffix = " [y/n]: "

    while True:
        ans = input(prompt + suffix).strip().lower()
        if not ans and default is not None:
            return default
        if ans in {"y", "yes"}:
            return True
        if ans in {"n", "no"}:
            return False
        print("Please answer 'y' or 'n'.")


def detect_environment() -> str:
    """Return a string describing the environment.

    Possible values:
    - "macos"
    - "ubuntu"
    - "wsl_ubuntu" (Ubuntu running under WSL)
    - "windows"
    - "other"
    """

    system = platform.system().lower()

    if system == "darwin":
        return "macos"

    if system == "windows":
        return "windows"

    if system == "linux":
        # Check for WSL
        try:
            with open("/proc/version", "r", encoding="utf-8") as f:
                ver = f.read().lower()
            if "microsoft" in ver or "wsl" in ver:
                # Distinguish Ubuntu-on-WSL vs other
                if Path("/etc/os-release").is_file():
                    data = Path("/etc/os-release").read_text(encoding="utf-8").lower()
                    if "ubuntu" in data:
                        return "wsl_ubuntu"
                return "other"
        except OSError:
            pass

        # Regular Linux, see if it's Ubuntu
        if Path("/etc/os-release").is_file():
            data = Path("/etc/os-release").read_text(encoding="utf-8").lower()
            if "ubuntu" in data:
                return "ubuntu"

        return "other"

    return "other"


def ensure_pyenv_in_env(env: Optional[dict] = None) -> dict:
    """Return an env dict with PYENV_ROOT and PATH set if ~/.pyenv exists.

    This is mostly for Linux / WSL manual installations.
    """

    if env is None:
        env = os.environ.copy()

    pyenv_root = os.environ.get("PYENV_ROOT") or str(Path.home() / ".pyenv")
    if Path(pyenv_root).is_dir():
        env["PYENV_ROOT"] = pyenv_root
        bin_dir = str(Path(pyenv_root) / "bin")
        if bin_dir not in env.get("PATH", ""):
            env["PATH"] = f"{bin_dir}:{env['PATH']}"
    return env


def command_exists(name: str, env: Optional[dict] = None) -> bool:
    return shutil.which(name, path=(env or os.environ).get("PATH")) is not None


# ------------------------ pyenv installation ------------------------


def install_pyenv_macos(env: dict) -> dict:
    print("\nDetected macOS.")
    if command_exists("pyenv", env):
        print("pyenv already appears to be installed.")
        return env

    print("\npyenv is not installed.")
    if not ask_yes_no("Install pyenv using Homebrew or the official installer?", default=True):
        print("Skipping pyenv installation at your request.")
        return env

    if command_exists("brew", env):
        print("\nInstalling pyenv and pyenv-virtualenv with Homebrew (you may be prompted for your password)...")
        try:
            run_cmd(["brew", "update"], check=True, env=env)
            run_cmd(["brew", "install", "pyenv", "pyenv-virtualenv"], check=True, env=env)
        except subprocess.CalledProcessError as e:
            print("Homebrew installation failed:", e)
        else:
            print("\npyenv and pyenv-virtualenv installed via Homebrew.")
    else:
        print(
            dedent(
                """
                Homebrew was not found on this system.

                The script can run the official pyenv installer, which will:
                - Download and install pyenv under ~/.pyenv
                - Print instructions for updating your shell configuration

                Command to be executed:
                  curl https://pyenv.run | bash
                """
            )
        )
        if ask_yes_no("Run the official pyenv installer now?", default=True):
            try:
                run_cmd("curl https://pyenv.run | bash", shell=True, check=True, env=env)
            except subprocess.CalledProcessError as e:
                print("pyenv installer failed:", e)
            else:
                print("\npyenv installer completed.")
        else:
            print("Skipping pyenv installation.")

    env = ensure_pyenv_in_env(env)
    return env


def append_to_shell_rc_if_missing(snippet: str) -> None:
    shell = os.environ.get("SHELL", "")
    home = Path.home()

    if shell.endswith("zsh"):
        rc = home / ".zshrc"
    else:
        # default to bash
        rc = home / ".bashrc"

    try:
        if rc.is_file():
            content = rc.read_text(encoding="utf-8")
            if "pyenv init" in content:
                return
        else:
            content = ""
    except OSError:
        return

    try:
        with rc.open("a", encoding="utf-8") as f:
            if not content.endswith("\n"):
                f.write("\n")
            f.write("\n" + snippet.strip("\n") + "\n")
        print(f"Appended pyenv init snippet to {rc}")
    except OSError as e:
        print(f"Could not update {rc}: {e}")


def install_pyenv_ubuntu_like(env: dict, *, is_wsl: bool) -> dict:
    if command_exists("pyenv", env):
        print("pyenv already appears to be installed.")
        return ensure_pyenv_in_env(env)

    print("\npyenv is not installed.")
    if not ask_yes_no("Install pyenv using git + apt (requires sudo)?", default=True):
        print("Skipping pyenv installation at your request.")
        return env

    # Install build dependencies
    print("\nInstalling build dependencies via apt (you may be prompted for your password)...")
    deps = [
        "build-essential",
        "curl",
        "git",
        "libssl-dev",
        "zlib1g-dev",
        "libbz2-dev",
        "libreadline-dev",
        "libsqlite3-dev",
        "llvm",
        "libncursesw5-dev",
        "xz-utils",
        "tk-dev",
        "libxml2-dev",
        "libxmlsec1-dev",
        "libffi-dev",
        "liblzma-dev",
    ]
    try:
        run_cmd(["sudo", "apt", "update"], check=True, env=env)
        run_cmd(["sudo", "apt", "install", "-y"] + deps, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print("apt installation failed:", e)

    pyenv_root = Path.home() / ".pyenv"
    if pyenv_root.is_dir():
        print(f"{pyenv_root} already exists; skipping git clone.")
    else:
        print("\nCloning pyenv into ~/.pyenv...")
        try:
            run_cmd(
                ["git", "clone", "https://github.com/pyenv/pyenv.git", str(pyenv_root)],
                check=True,
                env=env,
            )
        except subprocess.CalledProcessError as e:
            print("Git clone for pyenv failed:", e)

    # Optional: install pyenv-virtualenv plugin here too
    plugins_dir = pyenv_root / "plugins"
    virtualenv_dir = plugins_dir / "pyenv-virtualenv"
    if ask_yes_no("Install pyenv-virtualenv plugin as well?", default=True):
        plugins_dir.mkdir(parents=True, exist_ok=True)
        if virtualenv_dir.is_dir():
            print("pyenv-virtualenv plugin directory already exists; skipping clone.")
        else:
            print("Cloning pyenv-virtualenv plugin...")
            try:
                run_cmd(
                    [
                        "git",
                        "clone",
                        "https://github.com/pyenv/pyenv-virtualenv.git",
                        str(virtualenv_dir),
                    ],
                    check=True,
                    env=env,
                )
            except subprocess.CalledProcessError as e:
                print("Git clone for pyenv-virtualenv failed:", e)

    snippet = dedent(
        """
        # pyenv configuration
        export PYENV_ROOT="$HOME/.pyenv"
        command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init -)"
        if command -v pyenv-virtualenv-init >/dev/null 2>&1; then
          eval "$(pyenv virtualenv-init -)"
        fi
        """
    )
    append_to_shell_rc_if_missing(snippet)

    env = ensure_pyenv_in_env(env)
    print(
        "\npyenv installation steps finished. You may need to restart your shell "
        "or run 'exec $SHELL' for pyenv to be fully available in new terminals."
    )

    if is_wsl:
        print(
            "Detected Ubuntu under WSL. Make sure you always run this script *inside* "
            "your WSL/Ubuntu terminal (not in regular cmd.exe/PowerShell)."
        )

    return env


def ensure_pyenv_and_virtualenv(env_name: str, env: dict) -> dict:
    """Ensure pyenv is available; for Ubuntu/macOS also offer pyenv-virtualenv."""

    if env_name == "macos":
        env = install_pyenv_macos(env)
    elif env_name in {"ubuntu", "wsl_ubuntu"}:
        env = install_pyenv_ubuntu_like(env, is_wsl=(env_name == "wsl_ubuntu"))
    else:
        print("Unsupported environment for automatic pyenv installation.")

    env = ensure_pyenv_in_env(env)

    if not command_exists("pyenv", env):
        print("pyenv still not found in PATH. Please install/configure it manually and re-run this script.")
        return env

    # On macOS with Homebrew, pyenv-virtualenv may have been installed already
    if not command_exists("pyenv", env):
        return env

    # Check if pyenv-virtualenv is available
    try:
        run_cmd(["pyenv", "virtualenv", "--help"], check=True, capture_output=True, env=env)
        has_virtualenv = True
    except subprocess.CalledProcessError:
        has_virtualenv = False

    if not has_virtualenv:
        print("\npyenv-virtualenv does not appear to be available.")
        if env_name == "macos" and command_exists("brew", env):
            if ask_yes_no("Install pyenv-virtualenv with Homebrew now?", default=True):
                try:
                    run_cmd(["brew", "install", "pyenv-virtualenv"], check=True, env=env)
                    has_virtualenv = True
                except subprocess.CalledProcessError as e:
                    print("Failed to install pyenv-virtualenv via Homebrew:", e)
        elif env_name in {"ubuntu", "wsl_ubuntu"}:
            print(
                "If you previously declined the plugin installation, you can install it "
                "later with:\n"
                "  git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv\n"
            )

    return env


# ------------------------ version selection & installation ------------------------


def list_available_versions(env: dict) -> List[str]:
    print("\nRetrieving available CPython versions from pyenv (this may take a few seconds)...")
    try:
        out = run_cmd(
            ["pyenv", "install", "--list"], capture_output=True, check=True, env=env
        )
    except subprocess.CalledProcessError as e:
        print("Failed to list versions from pyenv:", e)
        return []

    versions: list[str] = []
    for line in out.splitlines():
        v = line.strip()
        if re.fullmatch(r"\d+\.\d+\.\d+", v):
            versions.append(v)

    if not versions:
        print("No CPython versions found in pyenv output.")
    return versions


def prompt_for_version(env: dict) -> Optional[str]:
    versions = list_available_versions(env)
    if not versions:
        return None

    # Show the most recent 15 versions
    latest = versions[-15:]
    print("\nSelect a Python version to install:")
    for i, v in enumerate(latest, start=1):
        print(f"  {i:2d}) {v}")

    print("\nYou can choose by number, or type an exact version (e.g. 3.12.4).")

    while True:
        choice = input("Your choice (or 'q' to quit): ").strip()
        if not choice:
            continue
        if choice.lower() in {"q", "quit", "exit"}:
            return None
        # Number
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(latest):
                return latest[idx]
            print("Please enter a number from the list above.")
            continue
        # Exact version
        if re.fullmatch(r"\d+\.\d+\.\d+", choice):
            if choice not in versions:
                if ask_yes_no(
                    f"Version {choice} was not in the recent list, but pyenv may still support it. Try installing it?",
                    default=True,
                ):
                    return choice
                continue
            return choice
        print("Please choose a valid number or a version like '3.12.4'.")


def ensure_version_installed(version: str, env: dict) -> bool:
    print(f"\nChecking if Python {version} is already installed via pyenv...")
    try:
        out = run_cmd(["pyenv", "versions", "--bare"], capture_output=True, check=True, env=env)
    except subprocess.CalledProcessError:
        out = ""

    installed = {line.strip() for line in out.splitlines() if line.strip()}
    if version in installed:
        print(f"Python {version} is already installed.")
        return True

    print(f"Python {version} is not installed. Starting installation (this may take a while)...")
    try:
        run_cmd(["pyenv", "install", version], check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"pyenv failed to install Python {version}: {e}")
        return False

    print(f"Python {version} installed successfully via pyenv.")
    return True


def maybe_set_global_version(version: str, env: dict) -> None:
    if ask_yes_no(
        f"Do you want to set Python {version} as your *global* default pyenv version?",
        default=False,
    ):
        try:
            run_cmd(["pyenv", "global", version], check=True, env=env)
            print(
                f"Global pyenv version set to {version}. New shells will use this version "
                "(unless overridden by a local version)."
            )
        except subprocess.CalledProcessError as e:
            print("Failed to set global pyenv version:", e)


# ------------------------ demo project with pyenv-virtualenv ------------------------


def create_demo_virtualenv(version: str, env: dict) -> None:
    print("\nSetting up a demo project using pyenv-virtualenv...")

    # Check if pyenv-virtualenv is available
    try:
        run_cmd(["pyenv", "virtualenv", "--help"], check=True, capture_output=True, env=env)
    except subprocess.CalledProcessError:
        print(
            "pyenv-virtualenv does not appear to be installed or configured. "
            "Skipping the demo virtualenv setup."
        )
        return

    home = Path.home()
    demo_dir = home / "pyenv_virtualenv_demo"
    env_name = "demo-env"

    demo_dir.mkdir(parents=True, exist_ok=True)

    print(f"Demo directory: {demo_dir}")
    print(f"Virtualenv name: {env_name}")

    # Create virtualenv if it doesn't exist yet
    try:
        out = run_cmd(["pyenv", "virtualenvs", "--bare"], capture_output=True, check=True, env=env)
        existing_envs = {line.strip() for line in out.splitlines() if line.strip()}
    except subprocess.CalledProcessError:
        existing_envs = set()

    full_env_name = env_name
    if full_env_name in existing_envs:
        print(f"Virtualenv '{env_name}' already exists; reusing it.")
    else:
        print(f"Creating virtualenv '{env_name}' for Python {version}...")
        try:
            run_cmd(["pyenv", "virtualenv", version, env_name], check=True, env=env)
        except subprocess.CalledProcessError as e:
            print("Failed to create virtualenv via pyenv-virtualenv:", e)
            return

    # Make this demo directory use the demo-env by default
    try:
        run_cmd(["pyenv", "local", env_name], check=True, env=env, cwd=str(demo_dir))
        print(
            f"Set local pyenv version for {demo_dir} to '{env_name}'. "
            "Any shell started in that directory will use this environment."
        )
    except subprocess.CalledProcessError as e:
        print("Failed to set local pyenv version in demo directory:", e)

    # Demonstrate activation in a subshell
    print(
        "\nNow demonstrating how activation works in a *subshell* (your current shell "
        "will not be modified):\n"
    )
    demo_cmd = f"cd '{demo_dir}' && pyenv activate {env_name} && echo 'Inside demo-env:' && python -V && which python && pyenv deactivate"
    try:
        run_cmd(["bash", "-lc", demo_cmd], check=True, env=env)
    except Exception as e:  # noqa: BLE001
        print("Subshell demonstration failed:", e)

    print(
        dedent(
            f"""
            \nManual steps you can try now (outside of this script):

              cd {demo_dir}
              pyenv activate {env_name}
              python -V
              which python
              pyenv deactivate

            When you 'cd' into {demo_dir}, pyenv will automatically select the
            '{env_name}' environment because of the .python-version file we created.
            """
        )
    )


# ------------------------ WSL / Windows guidance ------------------------


def print_windows_wsl_instructions() -> None:
    print(
        dedent(
            """
            Detected Windows (non-WSL) environment.

            This helper script is intended to run *inside* a Unix-like shell
            (macOS, Ubuntu, or Ubuntu under Windows Subsystem for Linux - WSL).

            To use it from Windows, follow these steps:

            1. Enable WSL (Windows Subsystem for Linux)

               - Open PowerShell **as Administrator** and run:

                   wsl --install -d Ubuntu

               - If you're on an older Windows 10 build and the above fails, try:

                   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
                   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

               - Restart your computer if prompted.

            2. Install an Ubuntu distribution from the Microsoft Store (if it
               wasn't installed automatically by 'wsl --install').

            3. Launch the Ubuntu (WSL) terminal, set up your Unix username, and
               then run this script **inside that Ubuntu shell**:

                   python3 python_env_setup.py

            Once you're inside Ubuntu/WSL, this script will treat it like a
            regular Ubuntu system and can install pyenv and pyenv-virtualenv for you.
            """
        )
    )


# ------------------------ main entry point ------------------------


def main() -> int:
    print_banner()

    env_name = detect_environment()
    raw_env = os.environ.copy()

    if env_name == "windows":
        print_windows_wsl_instructions()
        return 0

    if env_name == "other":
        print(
            "This script currently supports macOS and Ubuntu (including Ubuntu under WSL)."\
        )
        print("Your environment was detected as 'other'. Exiting.")
        return 1

    if env_name == "macos":
        print("Detected macOS.")
    elif env_name == "ubuntu":
        print("Detected Ubuntu.")
    elif env_name == "wsl_ubuntu":
        print("Detected Ubuntu running under Windows Subsystem for Linux (WSL).")

    env = ensure_pyenv_and_virtualenv(env_name, raw_env)

    if not command_exists("pyenv", env):
        # Already printed guidance inside ensure_pyenv_and_virtualenv
        return 1

    version = prompt_for_version(env)
    if not version:
        print("No version selected. Exiting.")
        return 0

    if not ensure_version_installed(version, env):
        print("Could not install the requested Python version. Exiting.")
        return 1

    maybe_set_global_version(version, env)

    if ask_yes_no("Create a demo project using pyenv-virtualenv?", default=True):
        create_demo_virtualenv(version, env)
    else:
        print("Skipping demo virtualenv creation.")

    print("\nAll done. You can re-run this script at any time to install other versions.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        raise SystemExit(1)
