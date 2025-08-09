import os
import subprocess
import platform
import sys
import shutil
from pathlib import Path


def is_nextclade_installed():
    """
    Checks if Nextclade is installed and accessible in the system's PATH.
    Returns True if installed, False otherwise.
    """
    try:
        # Attempt to run the `nextclade` command with the --version flag
        result = subprocess.run(["nextclade", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"Nextclade is installed: {result.stdout.decode().strip()}")
        return True
    except FileNotFoundError:
        print("Nextclade is not installed or not in PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error running Nextclade: {e}")
        return False
    
def install_nextclade():
    """
    Installs Nextclade for the appropriate platform and architecture, and ensures it's added to the PATH.
    """
    # Determine platform and architecture
    system = platform.system().lower()
    architecture = platform.machine().lower()
    
    # Map architectures to their respective Nextclade binaries (version 3.9.1)
    if system == "linux":
        if architecture == "x86_64":
            url = "https://github.com/nextstrain/nextclade/releases/download/3.9.1/nextclade-x86_64-unknown-linux-gnu"
        elif architecture == "aarch64":
            url = "https://github.com/nextstrain/nextclade/releases/download/3.9.1/nextclade-aarch64-unknown-linux-gnu"
        else:
            sys.exit(f"Unsupported architecture '{architecture}' on Linux.")
    elif system == "darwin":  # macOS
        if architecture == "x86_64":
            url = "https://github.com/nextstrain/nextclade/releases/download/3.9.1/nextclade-x86_64-apple-darwin"
        elif architecture == "arm64" or architecture == "aarch64":
            url = "https://github.com/nextstrain/nextclade/releases/download/3.9.1/nextclade-aarch64-apple-darwin"
        else:
            sys.exit(f"Unsupported architecture '{architecture}' on macOS.")
    elif system == "windows":
        if architecture == "x86_64":
            url = "https://github.com/nextstrain/nextclade/releases/download/3.9.1/nextclade-x86_64-pc-windows-gnu.exe"
        else:
            sys.exit(f"Unsupported architecture '{architecture}' on Windows.")
    else:
        sys.exit(f"Unsupported platform '{system}'.")

    # Define the installation path
    install_path = Path.home() / ".local" / "bin"
    install_path.mkdir(parents=True, exist_ok=True)
    nextclade_path = install_path / "nextclade"

    if system == "windows":
        nextclade_path = nextclade_path.with_suffix(".exe")  # Add .exe for Windows

    print(f"Downloading Nextclade from {url} to {nextclade_path}")

    # Download the Nextclade binary
    try:
        subprocess.run(["curl", "-L", url, "-o", str(nextclade_path)], check=True)
        nextclade_path.chmod(0o755)  # Make it executable
        print(f"Nextclade installed at {nextclade_path}")
    except Exception as e:
        sys.exit(f"Failed to install Nextclade: {e}")

    # Add the installation directory to the PATH dynamically and permanently
    dynamically_update_path(install_path)
    persist_path(install_path)
    link_into_venv_bin(nextclade_path)

def dynamically_update_path(install_path):
    """
    Dynamically updates the PATH environment variable for the current session.
    """
    os.environ["PATH"] = f"{install_path}:{os.environ.get('PATH')}"
    print(f"Dynamically added {install_path} to PATH for the current session.")

def persist_path(install_path):
    """
    Persists the installation directory in the PATH by appending it to the shell configuration file.
    """
    # Skip PATH persistence in Conda build environments
    if os.environ.get("CONDA_BUILD", "0") == "1":
        print("Running in a Conda build environment; skipping PATH persistence.")
        return
        
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        config_file = Path.home() / ".zshrc"
    elif "bash" in shell:
        config_file = Path.home() / ".bash_profile"
    elif "fish" in shell:
        config_file = Path.home() / ".config" / "fish" / "config.fish"
    else:
        sys.exit("Unsupported shell. Please add the following line to your shell configuration manually:\n"
                 f"export PATH={install_path}:$PATH")

    export_command = f'export PATH={install_path}:$PATH'

    try:
        # Check if the PATH is already added
        if config_file.exists():
            with open(config_file, "r") as file:
                if export_command in file.read():
                    print(f"PATH already configured in {config_file}.")
                    return

        # Append the export command to the shell config file
        with open(config_file, "a") as file:
            file.write(f"\n# Added by Nextclade installer\n{export_command}\n")

        print(f"Permanently added {install_path} to PATH in {config_file}.")
        print("Please restart your terminal or run `source` on your shell configuration file to apply the changes.")
    except Exception as e:
        sys.exit(f"Failed to persist PATH in {config_file}: {e}")

def link_into_venv_bin(tool_path: Path):
    """Place a symlink (or copy) of the tool into the current environment's bin directory if available.

    This ensures pip/venv users have the binary on PATH without modifying shell config.
    """
    try:
        if os.name == "nt":
            bin_dir = Path(sys.prefix) / "Scripts"
            target = bin_dir / tool_path.name
        else:
            bin_dir = Path(sys.prefix) / "bin"
            target = bin_dir / tool_path.name

        bin_dir.mkdir(parents=True, exist_ok=True)

        if not target.exists():
            try:
                os.symlink(tool_path, target)
            except OSError:
                shutil.copy2(tool_path, target)
        print(f"Linked {tool_path.name} into {bin_dir}")
    except Exception as e:
        print(f"Warning: could not link {tool_path.name} into environment bin: {e}")

if __name__ == "__main__":
    install_nextclade()
