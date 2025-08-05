#!/usr/bin/env python3
"""
Setup script for Verityn AI project.

This script helps initialize the project environment and install dependencies.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result


def check_uv_installed() -> bool:
    """Check if UV is installed."""
    try:
        result = run_command("uv --version", check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_python_version() -> bool:
    """Check if Python version is 3.12+."""
    version = sys.version_info
    return version.major == 3 and version.minor >= 12


def setup_environment():
    """Set up the project environment."""
    print("🚀 Setting up Verityn AI project...")
    
    # Check Python version
    if not check_python_version():
        print("❌ Error: Python 3.12+ is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Check if UV is installed
    if check_uv_installed():
        print("✅ UV is installed")
        setup_with_uv()
    else:
        print("⚠️  UV not found, using traditional pip")
        setup_with_pip()


def setup_with_uv():
    """Set up project using UV."""
    print("\n📦 Setting up with UV...")
    
    try:
        # Initialize UV project
        run_command("uv init --no-readme")
        
        # Install dependencies
        run_command("uv add --requirement requirements.txt")
        
        # Install development dependencies
        run_command("uv add --dev black isort flake8 mypy pytest")
        
        print("✅ UV setup completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during UV setup: {e}")
        sys.exit(1)


def setup_with_pip():
    """Set up project using traditional pip."""
    print("\n📦 Setting up with pip...")
    
    try:
        # Create virtual environment
        run_command("python3 -m venv .venv")
        
        # Activate virtual environment and install dependencies
        if os.name == 'nt':  # Windows
            activate_cmd = ".venv\\Scripts\\activate"
        else:  # Unix/Linux/macOS
            activate_cmd = "source .venv/bin/activate"
        
        run_command(f"{activate_cmd} && pip install --upgrade pip")
        run_command(f"{activate_cmd} && pip install -r requirements.txt")
        
        print("✅ Pip setup completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during pip setup: {e}")
        sys.exit(1)


def create_env_file():
    """Create .env file from template."""
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        print("\n📝 Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("✅ .env file created")
        print("⚠️  Please update .env file with your API keys")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  env.example not found, please create .env file manually")


def verify_setup():
    """Verify the setup was successful."""
    print("\n🔍 Verifying setup...")
    
    try:
        # Test imports
        test_imports = [
            "import openai",
            "import langchain",
            "import streamlit",
            "import fastapi",
            "import qdrant_client",
        ]
        
        for import_stmt in test_imports:
            run_command(f"python -c '{import_stmt}'")
        
        print("✅ All dependencies imported successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    return True


def main():
    """Main setup function."""
    print("🔍 Verityn AI - Project Setup")
    print("=" * 50)
    
    # Set up environment
    setup_environment()
    
    # Create .env file
    create_env_file()
    
    # Verify setup
    if verify_setup():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update .env file with your API keys")
        print("2. Start the backend: python backend/main.py")
        print("3. Start the frontend: streamlit run frontend/streamlit_app.py")
        print("\n📚 For more information, see README.md")
    else:
        print("\n❌ Setup verification failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 