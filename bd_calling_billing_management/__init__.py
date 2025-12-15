# from . import models
# from . import report
# from . import controllers
import os
import sys
import subprocess
import importlib.util
import logging

_logger = logging.getLogger(__name__)
# __init__.py
import os
import sys
import subprocess
import importlib.util
import logging

_logger = logging.getLogger(__name__)

def is_package_installed(package_name):
    """Check if a Python package is already installed"""
    try:
        # Remove version specifiers
        clean_name = package_name.split('>=')[0].split('==')[0].split('<=')[0].strip()
        
        # Check using importlib
        spec = importlib.util.find_spec(clean_name)
        if spec is None:
            return False
        
        # Special checks for specific packages
        if clean_name == 'pymupdf':
            try:
                import fitz
                return True
            except ImportError:
                return False
        elif clean_name == 'pdf2docx':
            try:
                from pdf2docx import Converter
                return True
            except ImportError:
                return False
                
        return True
    except Exception:
        return False

def install_from_requirements():
    """Auto-install packages from requirements.txt"""
    
    module_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(module_dir, 'requirements.txt')
    
    if not os.path.exists(requirements_file):
        _logger.warning("requirements.txt not found at %s", requirements_file)
        return False
    
    try:
        _logger.info("🔍 Checking dependencies from requirements.txt...")
        
        # Read requirements
        with open(requirements_file, 'r') as f:
            all_lines = f.readlines()
            requirements = []
            
            for line in all_lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
        
        if not requirements:
            _logger.info("No requirements found in requirements.txt")
            return True
        
        # Check which packages are missing
        missing_packages = []
        for req in requirements:
            if not is_package_installed(req):
                missing_packages.append(req)
        
        if not missing_packages:
            _logger.info("✅ All dependencies are already installed")
            return True
        
        _logger.info(f"📦 Installing {len(missing_packages)} missing packages...")
        
        # Install missing packages
        for package in missing_packages:
            _logger.info(f"Installing {package}...")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    check=True
                )
                _logger.info(f"✅ Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                _logger.error(f"❌ Failed to install {package}: {e.stderr}")
                return False
        
        _logger.info("🎉 All dependencies installed successfully!")
        return True
            
    except Exception as e:
        _logger.error(f"Error installing dependencies: {e}")
        return False

# Run installation when module loads
try:
    install_from_requirements()
except Exception as e:
    _logger.error(f"Error in dependency installation: {e}")
    
from . import models
from . import controllers
