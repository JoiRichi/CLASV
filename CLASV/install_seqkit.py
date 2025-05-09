import os
import subprocess
import platform
import sys
from pathlib import Path

def is_seqkit_installed():
    """
    Checks if SeqKit is installed and accessible in the system's PATH.
    Returns True if installed, False otherwise.
    """
    try:
        # Attempt to run the `seqkit` command with the `version` flag
        result = subprocess.run(["seqkit", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"SeqKit is installed: {result.stdout.decode().strip()}")
        return True
    except FileNotFoundError:
        print("SeqKit is not installed or not in PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error running SeqKit: {e}")
        return False


def install_seqkit():
    """
    Installs SeqKit for the appropriate platform and architecture, and ensures it's added to the PATH.
    """
    # Determine platform and architecture
    system = platform.system().lower()
    architecture = platform.machine().lower()
    
    # Map architectures to their respective SeqKit binaries (latest version v2.3.0 as of now)
    if system == "linux":
        if architecture == "x86_64":
            url = "https://github.com/shenwei356/seqkit/releases/download/v2.9.0/seqkit_linux_amd64.tar.gz"
        elif architecture == "aarch64":
            url = "https://github.com/shenwei356/seqkit/releases/download/v2.9.0/seqkit_linux_arm64.tar.gz"
        else:
            sys.exit(f"Unsupported architecture '{architecture}' on Linux.")
    elif system == "darwin":  # macOS
        if architecture == "x86_64":
            url = "https://github.com/shenwei356/seqkit/releases/download/v2.9.0/seqkit_darwin_amd64.tar.gz"
        elif architecture == "arm64":
            url = "https://github.com/shenwei356/seqkit/releases/download/v2.9.0/seqkit_darwin_arm64.tar.gz"
        else:
            sys.exit(f"Unsupported architecture '{architecture}' on macOS.")
    elif system == "windows":
        if architecture == "x86_64":
            url = "https://github.com/shenwei356/seqkit/releases/download/v2.9.0/seqkit_windows_amd64.exe.tar.gz"
        else:
            sys.exit(f"Unsupported architecture '{architecture}' on Windows.")
    else:
        sys.exit(f"Unsupported platform '{system}'.")

    # Define the installation path
    install_path = Path.home() / ".local" / "bin"
    install_path.mkdir(parents=True, exist_ok=True)
    seqkit_path = install_path / "seqkit"

    if system == "windows":
        seqkit_path = seqkit_path.with_suffix(".exe")  # Add .exe for Windows

    print(f"Downloading SeqKit from {url} to {seqkit_path}")

    # Download the SeqKit binary
    try:
        # Download and extract
        if url.endswith(".tar.gz"):
            subprocess.run(["curl", "-L", url, "-o", "seqkit.tar.gz"], check=True)
            subprocess.run(["tar", "-xvzf", "seqkit.tar.gz", "-C", str(install_path)], check=True)
            os.remove("seqkit.tar.gz")
        elif url.endswith(".zip"):
            subprocess.run(["curl", "-L", url, "-o", "seqkit.zip"], check=True)
            subprocess.run(["unzip", "seqkit.zip", "-d", str(install_path)], check=True)
            os.remove("seqkit.zip")
        else:
            sys.exit("Unknown file type for the binary.")

        # Make executable (for non-Windows systems)
        if not system == "windows":
            seqkit_path.chmod(0o755)

        print(f"SeqKit installed at {seqkit_path}")
    except Exception as e:
        sys.exit(f"Failed to install SeqKit: {e}")

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
            file.write(f"\n# Added by SeqKit installer\n{export_command}\n")

        print(f"Permanently added {install_path} to PATH in {config_file}.")
        print("Please restart your terminal or run `source` on your shell configuration file to apply the changes.")
    except Exception as e:
        sys.exit(f"Failed to persist PATH in {config_file}: {e}")

if __name__ == "__main__":
    if not is_seqkit_installed():
        install_seqkit()
    else:
        print("SeqKit is already installed.")
