#!/usr/bin/env python3
"""
Harbor System Check Script
Verifies all dependencies and system requirements for Harbor WebRTC streaming.
"""

import sys
import importlib
import platform
import subprocess
import pkg_resources
from pathlib import Path

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

def print_status(message, color=Colors.BLUE):
    print(f"{color}[INFO]{Colors.NC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def print_header(message):
    print(f"\n{Colors.WHITE}{'='*60}{Colors.NC}")
    print(f"{Colors.WHITE}{message.center(60)}{Colors.NC}")
    print(f"{Colors.WHITE}{'='*60}{Colors.NC}")

def check_python_version():
    """Check Python version compatibility."""
    print_header("Python Version Check")
    
    version = sys.version_info
    python_version = f"{version.major}.{version.minor}.{version.micro}"
    
    print_status(f"Python version: {python_version}")
    print_status(f"Platform: {platform.platform()}")
    print_status(f"Architecture: {platform.architecture()[0]}")
    
    if version.major == 3 and version.minor >= 8:
        print_success("✅ Python version is compatible")
        return True
    else:
        print_error("❌ Python 3.8+ is required")
        return False

def check_required_packages():
    """Check if all required packages are installed."""
    print_header("Required Package Check")
    
    required_packages = {
        'aiohttp': '3.8.0',
        'aiortc': '1.6.0',
        'av': '10.0.0',
        'numpy': '1.24.0'
    }
    
    missing_packages = []
    outdated_packages = []
    
    for package, min_version in required_packages.items():
        try:
            installed_version = pkg_resources.get_distribution(package).version
            print_status(f"{package}: {installed_version}")
            
            # Simple version comparison (works for most cases)
            if pkg_resources.parse_version(installed_version) >= pkg_resources.parse_version(min_version):
                print_success(f"✅ {package}: OK")
            else:
                print_warning(f"⚠️  {package}: Version {installed_version} < {min_version}")
                outdated_packages.append(f"{package}>={min_version}")
                
        except pkg_resources.DistributionNotFound:
            print_error(f"❌ {package}: NOT INSTALLED")
            missing_packages.append(f"{package}>={min_version}")
    
    if missing_packages or outdated_packages:
        print_error(f"Missing packages: {missing_packages}")
        print_warning(f"Outdated packages: {outdated_packages}")
        return False, missing_packages + outdated_packages
    else:
        print_success("✅ All required packages are installed and up to date")
        return True, []

def check_optional_packages():
    """Check optional packages for Raspberry Pi."""
    print_header("Optional Package Check (Raspberry Pi)")
    
    optional_packages = ['picamera2', 'gpiozero']
    pi_packages_available = []
    
    for package in optional_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print_success(f"✅ {package}: {version} (Pi hardware support)")
            pi_packages_available.append(package)
        except pkg_resources.DistributionNotFound:
            print_warning(f"⚠️  {package}: Not installed (demo mode will be used)")
    
    if pi_packages_available:
        print_success("✅ Raspberry Pi hardware support available")
    else:
        print_warning("⚠️  No Pi hardware support - demo mode only")
    
    return len(pi_packages_available) > 0

def check_harbor_modules():
    """Check if Harbor modules can be imported."""
    print_header("Harbor Module Check")
    
    harbor_modules = [
        ('harbor', 'Main harbor package'),
        ('harbor.led', 'LED controller'),
        ('harbor.video', 'Video streaming'),
        ('harbor.webrtc', 'WebRTC handling'),
        ('harbor.websocket', 'WebSocket commands'),
        ('harbor.client', 'Web client interface')
    ]
    
    failed_imports = []
    
    for module_name, description in harbor_modules:
        try:
            importlib.import_module(module_name)
            print_success(f"✅ {module_name}: {description}")
        except ImportError as e:
            print_error(f"❌ {module_name}: Import failed - {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print_error(f"Failed to import: {failed_imports}")
        return False
    else:
        print_success("✅ All Harbor modules imported successfully")
        return True

def check_network_tools():
    """Check for network diagnostic tools."""
    print_header("Network Tools Check")
    
    tools = ['lsof', 'netstat', 'curl']
    available_tools = []
    
    for tool in tools:
        try:
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"✅ {tool}: Available")
                available_tools.append(tool)
            else:
                print_warning(f"⚠️  {tool}: Not found (optional)")
        except Exception:
            print_warning(f"⚠️  {tool}: Check failed (optional)")
    
    return available_tools

def check_ssl_support():
    """Check SSL/TLS support for HTTPS."""
    print_header("SSL/TLS Support Check")
    
    try:
        import ssl
        print_success(f"✅ SSL module: Available")
        print_status(f"SSL version: {ssl.OPENSSL_VERSION}")
        
        # Check for openssl command
        try:
            result = subprocess.run(['openssl', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"✅ OpenSSL command: {result.stdout.strip()}")
                return True
            else:
                print_warning("⚠️  OpenSSL command not found (needed for certificate generation)")
                return False
        except Exception:
            print_warning("⚠️  OpenSSL command check failed")
            return False
            
    except ImportError:
        print_error("❌ SSL module not available")
        return False

def check_file_structure():
    """Check if all required files are present."""
    print_header("File Structure Check")
    
    required_files = [
        'app.py',
        'harbor/__init__.py',
        'harbor/client.py',
        'harbor/led.py',
        'harbor/video.py',
        'harbor/webrtc.py',
        'harbor/websocket.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"✅ {file_path}")
        else:
            print_error(f"❌ {file_path}: Missing")
            missing_files.append(file_path)
    
    if missing_files:
        print_error(f"Missing files: {missing_files}")
        return False
    else:
        print_success("✅ All required files present")
        return True

def generate_report():
    """Generate a comprehensive system report."""
    print_header("Harbor WebRTC System Check")
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", lambda: check_required_packages()[0]),
        ("Harbor Modules", check_harbor_modules),
        ("File Structure", check_file_structure),
        ("SSL Support", check_ssl_support),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print_error(f"Check '{check_name}' failed: {e}")
            results[check_name] = False
    
    # Optional checks
    check_optional_packages()
    check_network_tools()
    
    # Summary
    print_header("System Check Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.NC} {check_name}")
    
    print(f"\n{Colors.WHITE}Results: {passed}/{total} checks passed{Colors.NC}")
    
    if passed == total:
        print_success("🎉 System is ready for Harbor WebRTC streaming!")
        print_status("You can start the server with: python app.py")
        return True
    else:
        print_error("❌ System has issues that need to be resolved.")
        
        # Check for missing packages and provide install command
        pkg_check, missing = check_required_packages()
        if not pkg_check and missing:
            print_status("To install missing packages:")
            print(f"  pip install {' '.join(missing)}")
        
        return False

def main():
    """Main function."""
    try:
        success = generate_report()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\n⚠️  Check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
