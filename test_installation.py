"""
Installation Test Script
========================

Validates that all components are installed correctly.
"""

import sys
from pathlib import Path

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Print header."""
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{RESET}\n")


def test_python_version():
    """Test Python version."""
    print("1️⃣  Testing Python version...", end=" ")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 10:
        print(f"{GREEN}✓ OK{RESET} (Python {version.major}.{version.minor}.{version.micro})")
        return True
    else:
        print(f"{RED}✗ FAIL{RESET} (Python {version.major}.{version.minor}.{version.micro} < 3.10)")
        return False


def test_imports():
    """Test critical imports."""
    print("2️⃣  Testing dependencies...")
    
    packages = [
        ('playwright', 'Playwright'),
        ('yaml', 'PyYAML'),
        ('typer', 'Typer'),
        ('rich', 'Rich'),
        ('streamlit', 'Streamlit'),
        ('loguru', 'Loguru'),
        ('aiosqlite', 'aiosqlite'),
        ('httpx', 'HTTPX'),
    ]
    
    all_ok = True
    
    for module, name in packages:
        try:
            __import__(module)
            print(f"   {GREEN}✓{RESET} {name}")
        except ImportError:
            print(f"   {RED}✗{RESET} {name} (not installed)")
            all_ok = False
    
    return all_ok


def test_project_structure():
    """Test project structure."""
    print("\n3️⃣  Testing project structure...")
    
    required_paths = [
        'core/__init__.py',
        'core/browser.py',
        'core/crawler.py',
        'core/interceptor.py',
        'core/database.py',
        'utils/__init__.py',
        'utils/proxy.py',
        'utils/normalization.py',
        'utils/robots.py',
        'dashboard/app.py',
        'config/default.yaml',
        'main.py',
        'requirements.txt',
    ]
    
    all_ok = True
    
    for path in required_paths:
        file_path = Path(path)
        if file_path.exists():
            print(f"   {GREEN}✓{RESET} {path}")
        else:
            print(f"   {RED}✗{RESET} {path} (missing)")
            all_ok = False
    
    return all_ok


def test_config():
    """Test configuration file."""
    print("\n4️⃣  Testing configuration...", end=" ")
    
    try:
        import yaml
        with open('config/default.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        required = ['scraping', 'database', 'logging']
        for key in required:
            if key not in config:
                print(f"{RED}✗ FAIL{RESET} (missing: {key})")
                return False
        
        print(f"{GREEN}✓ OK{RESET}")
        return True
        
    except Exception as e:
        print(f"{RED}✗ FAIL{RESET} ({e})")
        return False


def test_directories():
    """Test directory permissions."""
    print("\n5️⃣  Testing directory permissions...", end=" ")
    
    try:
        dirs = ['data', 'logs', 'exports', 'data/backups']
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        print(f"{GREEN}✓ OK{RESET}")
        return True
        
    except Exception as e:
        print(f"{RED}✗ FAIL{RESET} ({e})")
        return False


def test_playwright():
    """Test Playwright installation."""
    print("\n6️⃣  Testing Playwright...", end=" ")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        
        print(f"{GREEN}✓ OK{RESET}")
        return True
        
    except Exception as e:
        print(f"{RED}✗ FAIL{RESET}")
        print(f"   {YELLOW}→ Run: playwright install chromium{RESET}")
        return False


def main():
    """Main test runner."""
    print_header("🧪 API Scraper Pro - Installation Test")
    
    tests = [
        test_python_version,
        test_imports,
        test_project_structure,
        test_config,
        test_directories,
        test_playwright,
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"{RED}✗ Test error: {e}{RESET}")
            results.append(False)
    
    # Summary
    print_header("📊 Summary")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {GREEN}{passed}/{total}{RESET}")
    print(f"Failed: {RED}{total - passed}/{total}{RESET}")
    
    if all(results):
        print(f"\n{GREEN}🎉 All tests passed! Ready to use.{RESET}")
        print(f"\n{BLUE}Next steps:{RESET}")
        print(f"   1. Read QUICKSTART.md")
        print(f"   2. Run: python main.py scrape https://jsonplaceholder.typicode.com")
        print(f"   3. View results: python main.py dashboard")
        return 0
    else:
        print(f"\n{RED}⚠️  Some tests failed.{RESET}")
        print(f"\n{YELLOW}Fix suggestions:{RESET}")
        print(f"   1. Install missing dependencies: pip install -r requirements.txt")
        print(f"   2. Install Playwright: playwright install chromium")
        print(f"   3. Check Python version: python --version (need 3.10+)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
