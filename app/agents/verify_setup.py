"""
Setup verification script for the Context Manager Agent System.

This script checks that all dependencies are installed correctly
and that the required environment variables are configured.
"""

import sys
import os


def check_package(package_name: str, import_name: str = None) -> bool:
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        return False


def check_env_var(var_name: str, optional: bool = False) -> bool:
    """Check if an environment variable is set."""
    value = os.getenv(var_name)
    
    if value:
        # Mask sensitive values
        if "TOKEN" in var_name or "KEY" in var_name:
            masked_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            masked_value = value
        
        print(f"✅ {var_name} is set: {masked_value}")
        return True
    else:
        if optional:
            print(f"⚠️  {var_name} is NOT set (optional)")
            return True
        else:
            print(f"❌ {var_name} is NOT set (required)")
            return False


def main():
    """Run all verification checks."""
    print("\n" + "="*80)
    print("CONTEXT MANAGER AGENT - SETUP VERIFICATION")
    print("="*80 + "\n")
    
    all_checks_passed = True
    
    # Check Python version
    print("📋 Checking Python version...")
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} (>= 3.8 required)")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (>= 3.8 required)")
        all_checks_passed = False
    
    print("\n" + "-"*80)
    
    # Check required packages
    print("\n📦 Checking required packages...")
    packages = [
        ("llama-index-core", "llama_index.core"),
        ("llama-index-llms-openai", "llama_index.llms.openai"),
        ("PyGithub", "github"),
        ("python-dotenv", "dotenv"),
        ("openai", "openai"),
    ]
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_checks_passed = False
    
    print("\n" + "-"*80)
    
    # Load .env file
    print("\n🔧 Loading environment variables...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env file loaded")
    except Exception as e:
        print(f"⚠️  Could not load .env file: {e}")
    
    print("\n" + "-"*80)
    
    # Check required environment variables
    print("\n🔑 Checking environment variables...")
    required_vars = [
        "GITHUB_TOKEN",
        "OPENAI_API_KEY",
    ]
    
    optional_vars = [
        "OPENAI_MODEL",
        "OPENAI_BASE_URL",
    ]
    
    for var in required_vars:
        if not check_env_var(var):
            all_checks_passed = False
    
    for var in optional_vars:
        check_env_var(var, optional=True)
    
    print("\n" + "-"*80)
    
    # Try to import the agent module
    print("\n🤖 Checking agent module...")
    try:
        # Add the project root to Python path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from app.agents.context_agent import context_agent, get_pr_details
        print("✅ Agent module can be imported")
        print(f"✅ Agent tools: {len(context_agent.get_tools())} tools available")
    except Exception as e:
        print(f"❌ Agent module import failed: {e}")
        all_checks_passed = False
    
    print("\n" + "="*80)
    
    # Final summary
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED! Your setup is ready to use.")
        print("\nNext steps:")
        print("1. Run the agent: python3 app/agents/context_agent.py")
        print("2. Try examples: python3 app/agents/examples.py")
        print("3. Or use it programmatically in your code")
    else:
        print("❌ SOME CHECKS FAILED! Please fix the issues above.")
        print("\nTo install missing packages:")
        print("  pip install -r app/agents/requirements.txt")
        print("\nTo configure environment variables:")
        print("  Edit the .env file in your project root")
    
    print("="*80 + "\n")
    
    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    sys.exit(main())
