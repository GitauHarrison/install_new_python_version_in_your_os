# Python Version & `pyenv-virtualenv` Setup Helper

This repository contains a single Python script, `python_env_setup.py`, that automates much of the setup needed to install a newer version of Python on your system using [`pyenv`](https://github.com/pyenv/pyenv) and, optionally, [`pyenv-virtualenv`](https://github.com/pyenv/pyenv-virtualenv).

It is designed to be **interactive** and to work on:
- **macOS**
- **Ubuntu Linux**
- **Ubuntu running under Windows Subsystem for Linux (WSL)**

On plain (non-WSL) Windows, the script will show you how to enable WSL and install Ubuntu so that you can then run the script inside that environment.

If you specifically want to **learn how to work with `pyenv` and `pyenv-virtualenv` on macOS step by step**, you can also refer to this companion guide:

- [Using a newer Python version on macOS with pyenv & virtualenv](https://github.com/GitauHarrison/notes_on_general_topics/blob/main/01_new_python_version_macOS_virtualenv.md)

---

## Table of Contents

- [What this script does](#what-this-script-does)
- [Prerequisites](#prerequisites)
- [Getting started](#getting-started)
- [Platform-specific notes](#platform-specific-notes)
  - [macOS](#macos)
  - [Ubuntu and Ubuntu under WSL](#ubuntu-and-ubuntu-under-wsl)
  - [Plain Windows (non-WSL)](#plain-windows-non-wsl)
- [Understanding how `python` behaves with pyenv](#understanding-how-python-behaves-with-pyenv)
- [The interactive flow](#the-interactive-flow)
- [Notes and limitations](#notes-and-limitations)
- [Uninstalling or cleaning up the demo](#uninstalling-or-cleaning-up-the-demo)
- [Troubleshooting](#troubleshooting)

---

## What this script does

When you run `python_env_setup.py`, it will:

1. **Detect your environment**
   - macOS
   - Ubuntu
   - Ubuntu under WSL
   - or plain Windows (for WSL instructions only)

2. **Offer to install `pyenv`** (and optionally `pyenv-virtualenv`)
   - On macOS, it prefers Homebrew but can also run the official `pyenv` installer.
   - On Ubuntu/WSL, it installs required build dependencies via `apt` and clones `pyenv` into `~/.pyenv`, optionally installing `pyenv-virtualenv` as a plugin.

3. **List recent CPython versions** available through `pyenv`
   - You see a numbered list of recent stable versions (e.g. `3.13.x`, `3.12.x`, `3.11.x`, ...).
   - You can select by **number** or type a **specific version** like `3.12.4`.

4. **Install the version you chose** with `pyenv`
   - If that version is already installed, it skips the build.
   - Otherwise, it runs `pyenv install <version>` and shows progress in your terminal.

5. **Optionally set that version as your global default**
   - If you say "yes", the script runs `pyenv global <version>`.
   - New shells will then use this version as the default (unless a project overrides it with a local version).

6. **Optionally create a demo project using `pyenv-virtualenv`**
   - In your home directory, it creates a folder: `~/pyenv_virtualenv_demo`.
   - It creates a virtual environment called `demo-env` for the Python version you selected.
   - It runs `pyenv local demo-env` in the demo folder, so **any shell** you open in that folder will automatically use that environment.
   - It also runs a short **subshell demo** to show `python -V` and `which python` from inside `demo-env`.

Throughout, the script is **prompt-driven**: it asks you to confirm important steps and allows you to skip things if you prefer to do them manually.

---

## Prerequisites

You need:

- **Git** (for cloning this repository and, on Ubuntu, for cloning `pyenv` and `pyenv-virtualenv`).
- **Python 3.6 or newer** installed and accessible as `python3` on your PATH.
  - macOS usually has a system `python3`, or you may have installed one via Homebrew or Xcode tools.
  - Ubuntu and Ubuntu/WSL typically include a recent enough `python3` by default.
  - On significantly older distributions where `python3` < 3.6 is the default, please upgrade Python first (the script uses modern language features such as f-strings).

If `python3` is not available, install it first on your platform (e.g. `brew install python` on macOS, `sudo apt install python3` on Ubuntu, or `wsl --install` on Windows to get an Ubuntu environment that comes with Python 3).

---

## Getting started

### 1. Clone this repository

```bash
git clone <YOUR_REPO_URL>
cd <YOUR_REPO_DIR>
```

> Replace `<YOUR_REPO_URL>` and `<YOUR_REPO_DIR>` with the actual URL and directory name of this repository.

### 2. Run the script

You can either run it directly with Python (recommended and works regardless of file permissions), or optionally mark it as executable on your own machine.

**Option A: Run with Python (no permission changes needed)**

```bash
python3 python_env_setup.py
```

This works even if the file is not marked as executable (the default `rw-r--r--` / `644` mode in most clones).

**Option B: Make it executable and run it**

```bash
chmod +x python_env_setup.py
./python_env_setup.py
```

If you choose this option, a typical, sensible mode is `755` (owner can read/write/execute; others can read/execute). There is usually **no need** to change it to `700` or `600`:

- `700` would restrict execution to just the current user, which is fine but not necessary for a script in a shared repo.
- `600` would make the file non-executable (no `x` bit) and also unreadable to other users, so it is not appropriate for a script you want to run.

In short: you can leave permissions as they are after cloning, use Option A, and only use `chmod +x` locally if you prefer `./python_env_setup.py` style.

You will see a banner and a series of prompts guiding you through the process.

---

## Platform-specific notes

### macOS

On macOS, the script:

1. Detects that you're on macOS.
2. Checks if `pyenv` is already installed.
3. If not, it offers two installation paths:
   - **Using Homebrew** (preferred):
     - `brew update`
     - `brew install pyenv pyenv-virtualenv`
   - **Using the official `pyenv` installer**:
     - Runs `curl https://pyenv.run | bash` after you confirm.
4. Updates its own environment so that `pyenv` is usable immediately from within the script.

> Note: Depending on how your shell is configured (e.g. `zsh` with `~/.zshrc` or `bash` with `~/.bashrc`), you might need to add the `pyenv` initialization snippet to your shell rc file. Homebrew and the `pyenv` installer will print suggestions. The script attempts to help with configuration on Linux; on macOS you may still want to verify your shell rc file manually.

Once `pyenv` is available, the remaining steps (version selection, installation, and demo virtualenv) behave the same as on Ubuntu.

---

### Ubuntu and Ubuntu under WSL

On **Ubuntu** (including **Ubuntu on WSL**), the script:

1. Detects your environment as `ubuntu` or `wsl_ubuntu`.
2. Checks if `pyenv` is already installed.
3. If not, it asks whether to:
   - Install required build dependencies with `apt` (e.g. `build-essential`, `libssl-dev`, `zlib1g-dev`, etc.).
   - Clone `pyenv` into `~/.pyenv` with `git clone`.
   - Optionally clone the `pyenv-virtualenv` plugin into `~/.pyenv/plugins/pyenv-virtualenv`.
4. Appends a standard `pyenv` initialization snippet to your shell rc (e.g. `~/.bashrc` or `~/.zshrc`) if it does not already contain `pyenv init`.
5. Updates its own environment so that `pyenv` can be used immediately by this script.

If you're using **WSL (Windows Subsystem for Linux)**:

- Make sure you are running this script **inside** your Ubuntu/WSL terminal, not in `cmd.exe` or PowerShell.
- The script treats WSL Ubuntu like regular Ubuntu, but it will print a reminder that you must always run it in the WSL/Ubuntu environment.

---

### Plain Windows (non-WSL)

If you run `python_env_setup.py` directly on **Windows** (outside of WSL), the script:

1. Detects that you're on Windows.
2. Prints instructions for enabling **Windows Subsystem for Linux (WSL)** and installing Ubuntu.
3. Exits without making changes.

**Summary of WSL steps (the script will show these too):**

1. Open **PowerShell as Administrator**.
2. Run:

   ```powershell
   wsl --install -d Ubuntu
   ```

   - On older Windows 10 builds, if `wsl --install` fails, you may need to run:

     ```powershell
     dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
     dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
     ```

3. Restart your computer if prompted.
4. Launch the **Ubuntu** app from the Start menu.
5. In the Ubuntu terminal, clone this repo and run:

   ```bash
   python3 python_env_setup.py
   ```

From this point on, the script behaves as if you were on a regular Ubuntu system.

---

## Understanding how `python` behaves with pyenv

A very common point of confusion is that **`python -V` can show different versions depending on where you are and how pyenv is configured**. This is expected.

### 1. Local (per-project) version via `.python-version`

When the script creates the demo project, it does this inside `~/pyenv_virtualenv_demo`:

- Creates a virtual environment, e.g. `demo-env`.
- Runs:
  ```bash
  pyenv local demo-env
  ```
- This writes a `.python-version` file containing `demo-env` into that directory.

What this means in practice:

- **Inside** `~/pyenv_virtualenv_demo`:
  - `python -V` and `python3 -V` will use the Python from `demo-env` (e.g. `3.14.2`).
  - `which python` will point to something like `~/.pyenv/versions/demo-env/bin/python`.
  - `pyenv version` will show:
    ```text
    demo-env (set by /home/you/pyenv_virtualenv_demo/.python-version)
    ```
- **Outside** that directory (e.g. `cd ~` or `cd /tmp`):
  - The `.python-version` file is no longer in effect.
  - `python -V` and `python3 -V` fall back to either your **global pyenv version** or your **system Python**.

So it is **normal** and **not a problem** if:

- `python -V` inside the demo folder shows your new pyenv-managed version.
- `python -V` outside the demo folder shows your system Python (for example `3.8.10`).

### 2. Global pyenv version vs system Python

pyenv distinguishes between:

- The **system** Python (whatever your OS ships, e.g. `/usr/bin/python` or `/usr/bin/python3`).
- The **global pyenv version**, which you can set with `pyenv global`.

To see what pyenv thinks is active in the current directory:

```bash
pyenv version
```

Typical outputs:

- `demo-env (set by /home/you/pyenv_virtualenv_demo/.python-version)` → project-local env is active.
- `3.14.2 (set by /home/you/.pyenv/version)` → a pyenv-managed global version is active.
- `system (set by /home/you/.pyenv/version)` → pyenv is active but defers to the OS Python.

### 3. Making your new Python the global default (optional)

If, after using the script, you want **all shells, in all directories** to default to your new version (for example `3.14.2`) instead of the system Python, run:

```bash
pyenv global 3.14.2
exec "$SHELL" -l   # restart your shell to pick up the change
```

Now, outside any directory with a `.python-version` file:

- `python -V` → `Python 3.14.2`
- `python3 -V` → `Python 3.14.2`
- `which python` → will resolve to pyenv's shim, which then maps to `~/.pyenv/versions/3.14.2/bin/python`.

Inside a project with its own `.python-version` (like the demo directory), the **local** setting still wins over the global setting.

If you ever want to go back to using the OS Python as the default, you can run:

```bash
pyenv global system
exec "$SHELL" -l
```

After that, outside any pyenv-managed project directory:

- `python -V` / `python3 -V` will again show your system version (e.g. `3.8.10`).

### 4. Quick checklist when versions look “wrong”

If `python -V` does not show what you expect, check in this order:

1. **Are you in a directory with a `.python-version` file?**
   - Run `pwd` and `ls -a` to see if `.python-version` is present.
   - If yes, run `pyenv version` to see which environment it is selecting.
2. **What is your global pyenv setting?**
   - Run `pyenv global`.
3. **Is pyenv active at all?**
   - Run `type pyenv` — it should say `pyenv is a function` or similar.
   - Run `which python` — it should go through pyenv's shims (usually under `~/.pyenv/shims`).

Understanding these three layers (local `.python-version`, global pyenv version, and system Python) explains almost all “why is `python -V` showing X instead of Y?” questions.

---

## The interactive flow

Here is what a typical session might look like once you run:

```bash
python3 python_env_setup.py
```

1. **Environment detection**

   - Script prints something like:

     ```text
     Python version & pyenv-virtualenv setup helper

     Detected Ubuntu.
     ```

2. **pyenv installation**

   - If `pyenv` is not installed, you might see:

     ```text
     pyenv is not installed.
     Install pyenv using git + apt (requires sudo)? [Y/n]:
     ```

   - Answer `Y` (or press Enter) to let the script install dependencies and clone `pyenv` for you.

3. **Version selection**

   - After setting up `pyenv`, the script runs `pyenv install --list` and shows something like:

     ```text
     Select a Python version to install:
       1) 3.11.9
       2) 3.12.3
       3) 3.13.0

     You can choose by number, or type an exact version (e.g. 3.12.4).
     Your choice (or 'q' to quit):
     ```

   - You can type `3` or `3.13.0` directly, or any exact version you know `pyenv` supports.

4. **Installing the selected version**

   - If the version is not yet installed, the script runs:

     ```bash
     pyenv install <version>
     ```

   - This may take several minutes the first time, since it builds Python from source.

5. **Setting the global version (optional)**

   - After installation, you'll see a prompt like:

     ```text
     Do you want to set Python 3.13.0 as your *global* default pyenv version? [y/N]:
     ```

   - If you choose `y`, the script runs `pyenv global 3.13.0` for you.

6. **Demo project with `pyenv-virtualenv` (optional)**

   - If `pyenv-virtualenv` is available, the script then asks:

     ```text
     Create a demo project using pyenv-virtualenv? [Y/n]:
     ```

   - If you choose `Y`, it will:
     - Create `~/pyenv_virtualenv_demo`.
     - Create a virtualenv named `demo-env` for the selected Python version.
     - Run `pyenv local demo-env` inside that directory.
     - Run a short demonstration in a subshell, showing `python -V` and `which python` inside the environment.

7. **Instructions for manual activation/deactivation**

   - Finally, it prints clear instructions similar to:

     ```text
     Manual steps you can try now (outside of this script):

       cd /home/youruser/pyenv_virtualenv_demo
       pyenv activate demo-env
       python -V
       which python
       pyenv deactivate

     When you 'cd' into /home/youruser/pyenv_virtualenv_demo, pyenv will
     automatically select the 'demo-env' environment because of the
     .python-version file we created.
     ```

---

## Notes and limitations

- The script cannot permanently change the environment of your **current** shell session; it can only:
  - Show you what commands to run.
  - Demonstrate activation in a **subshell**.
  - Set configuration files (like `~/.bashrc`) so that future shells behave correctly.

- On Ubuntu/WSL, the script appends a standard `pyenv` initialization snippet to your shell rc file (usually `~/.bashrc` or `~/.zshrc`) **if it does not already contain `pyenv init`**. You can review or adjust this snippet if you have a custom shell setup.

- If you prefer **manual installation**, you can skip all automated steps by answering `n` to the prompts. The script will still help you:
  - List available Python versions via `pyenv`.
  - Install a chosen version.
  - Optionally create a demo environment once you have `pyenv-virtualenv` configured.

- This script focuses on **CPython** versions (the standard Python implementation). It filters out most non-version entries from `pyenv install --list` and shows you recent stable releases.

---

## Uninstalling or cleaning up the demo

If you want to remove the demo folder and virtual environment created by this script:

1. Delete the demo directory:

   ```bash
   rm -rf ~/pyenv_virtualenv_demo
   ```

2. Remove the virtualenv from `pyenv-virtualenv` (if you no longer need it):

   ```bash
   pyenv uninstall demo-env
   ```

3. If you no longer want `pyenv` itself, follow the official instructions from the `pyenv` and `pyenv-virtualenv` repositories to remove them and clean up any configuration snippets.

---

## Troubleshooting

- **`pyenv: command not found` even after installation**
  - Make sure your shell rc file (e.g. `~/.bashrc` or `~/.zshrc`) contains the `pyenv` initialization snippet and that you have restarted your shell or run `exec $SHELL`.

- **`pyenv install` fails**
  - Check that all build dependencies are installed (the script tries to install a comprehensive set on Ubuntu).
  - Read the error messages in the terminal; sometimes missing libraries or incompatible compilers are the cause.

- **`pyenv-virtualenv` commands not found**
  - Ensure that the `pyenv-virtualenv` plugin directory exists under `~/.pyenv/plugins/pyenv-virtualenv` (for the git-based install), or that you've installed `pyenv-virtualenv` via your package manager (e.g. Homebrew).

If you encounter issues that this script does not handle well, you can always fall back to the official documentation for `pyenv` and `pyenv-virtualenv` and perform the steps manually.
