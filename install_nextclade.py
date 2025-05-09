import os
import subprocess
import platform
import sys
from pathlib import Path

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

if __name__ == "__main__":
    install_nextclade()
