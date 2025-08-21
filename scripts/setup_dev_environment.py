#!/usr/bin/env python3
"""
Advanced Development Environment Setup Script for GLPI Dashboard

This script sets up a complete development environment with:
- Security tools and configurations
- Code quality tools
- Pre-commit hooks
- Development dependencies
- Environment validation

Usage:
    python scripts/setup_dev_environment.py [--full] [--security-only] [--validate]
"""

import os
import sys
import subprocess
import json
import argparse
import platform
from pathlib import Path
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup_dev_environment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DevEnvironmentSetup:
    """Advanced development environment setup with security focus."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.scripts_dir = self.project_root / "scripts"
        self.is_windows = platform.system() == "Windows"
        
        # Tool versions
        self.tool_versions = {
            "python": "3.11+",
            "node": "18+",
            "npm": "9+",
            "git": "2.30+"
        }
        
        # Security tools to install
        self.security_tools = {
            "python": [
                "bandit[toml]",
                "safety",
                "pip-audit",
                "detect-secrets",
                "semgrep",
                "ggshield",
                "pip-licenses"
            ],
            "node": [
                "@npmcli/arborist",
                "audit-ci",
                "snyk",
                "eslint-plugin-security"
            ]
        }
        
        # Quality tools
        self.quality_tools = {
            "python": [
                "black",
                "isort",
                "flake8",
                "mypy",
                "pylint",
                "pytest",
                "pytest-cov",
                "pytest-xdist",
                "pytest-mock",
                "radon",
                "pre-commit"
            ],
            "node": [
                "eslint",
                "prettier",
                "@typescript-eslint/parser",
                "@typescript-eslint/eslint-plugin",
                "husky",
                "lint-staged"
            ]
        }
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None, 
                   check: bool = True) -> subprocess.CompletedProcess:
        """Run a command with proper error handling."""
        try:
            logger.info(f"Running: {' '.join(command)}")
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=check
            )
            if result.stdout:
                logger.debug(f"Output: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(command)}")
            logger.error(f"Error: {e.stderr}")
            raise
    
    def check_prerequisites(self) -> bool:
        """Check if all required tools are installed."""
        logger.info("Checking prerequisites...")
        
        checks = {
            "python": ["python", "--version"],
            "pip": ["pip", "--version"],
            "node": ["node", "--version"],
            "npm": ["npm", "--version"],
            "git": ["git", "--version"]
        }
        
        missing_tools = []
        
        for tool, command in checks.items():
            try:
                result = self.run_command(command, check=False)
                if result.returncode == 0:
                    logger.info(f"✓ {tool}: {result.stdout.strip()}")
                else:
                    missing_tools.append(tool)
                    logger.error(f"✗ {tool}: Not found")
            except FileNotFoundError:
                missing_tools.append(tool)
                logger.error(f"✗ {tool}: Not found")
        
        if missing_tools:
            logger.error(f"Missing required tools: {', '.join(missing_tools)}")
            return False
        
        return True
    
    def setup_python_environment(self, security_only: bool = False) -> bool:
        """Set up Python development environment."""
        logger.info("Setting up Python environment...")
        
        try:
            # Create virtual environment if it doesn't exist
            venv_path = self.project_root / "venv"
            if not venv_path.exists():
                logger.info("Creating virtual environment...")
                self.run_command(["python", "-m", "venv", "venv"])
            
            # Activate virtual environment
            if self.is_windows:
                pip_cmd = [str(venv_path / "Scripts" / "pip.exe")]
                python_cmd = [str(venv_path / "Scripts" / "python.exe")]
            else:
                pip_cmd = [str(venv_path / "bin" / "pip")]
                python_cmd = [str(venv_path / "bin" / "python")]
            
            # Upgrade pip
            self.run_command(pip_cmd + ["install", "--upgrade", "pip"])
            
            # Install backend requirements
            if (self.backend_dir / "requirements.txt").exists():
                logger.info("Installing backend requirements...")
                self.run_command(pip_cmd + ["install", "-r", str(self.backend_dir / "requirements.txt")])
            
            # Install security tools
            logger.info("Installing security tools...")
            for tool in self.security_tools["python"]:
                self.run_command(pip_cmd + ["install", tool])
            
            # Install quality tools (unless security-only)
            if not security_only:
                logger.info("Installing quality tools...")
                for tool in self.quality_tools["python"]:
                    self.run_command(pip_cmd + ["install", tool])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Python environment: {e}")
            return False
    
    def setup_node_environment(self, security_only: bool = False) -> bool:
        """Set up Node.js development environment."""
        logger.info("Setting up Node.js environment...")
        
        try:
            # Install frontend dependencies
            if (self.frontend_dir / "package.json").exists():
                logger.info("Installing frontend dependencies...")
                self.run_command(["npm", "ci"], cwd=self.frontend_dir)
            
            # Install security tools globally
            logger.info("Installing security tools...")
            for tool in self.security_tools["node"]:
                self.run_command(["npm", "install", "-g", tool])
            
            # Install quality tools (unless security-only)
            if not security_only:
                logger.info("Installing quality tools...")
                for tool in self.quality_tools["node"]:
                    self.run_command(["npm", "install", "-g", tool])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Node.js environment: {e}")
            return False
    
    def setup_pre_commit_hooks(self) -> bool:
        """Set up pre-commit hooks."""
        logger.info("Setting up pre-commit hooks...")
        
        try:
            # Install pre-commit hooks
            if (self.project_root / ".pre-commit-config.yaml").exists():
                self.run_command(["pre-commit", "install"])
                self.run_command(["pre-commit", "install", "--hook-type", "commit-msg"])
                self.run_command(["pre-commit", "install", "--hook-type", "pre-push"])
                
                # Run pre-commit on all files to ensure everything works
                logger.info("Running pre-commit on all files...")
                result = self.run_command(["pre-commit", "run", "--all-files"], check=False)
                if result.returncode != 0:
                    logger.warning("Some pre-commit hooks failed. This is normal for initial setup.")
                
                return True
            else:
                logger.warning(".pre-commit-config.yaml not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup pre-commit hooks: {e}")
            return False
    
    def create_security_baseline(self) -> bool:
        """Create security baseline files."""
        logger.info("Creating security baseline files...")
        
        try:
            # Create secrets baseline
            logger.info("Creating secrets baseline...")
            result = self.run_command([
                "detect-secrets", "scan", "--baseline", ".secrets.baseline"
            ], check=False)
            
            if result.returncode == 0:
                logger.info("✓ Secrets baseline created")
            else:
                logger.warning("Could not create secrets baseline")
            
            # Create bandit baseline
            logger.info("Creating bandit baseline...")
            result = self.run_command([
                "bandit", "-r", "backend/", "-f", "json", "-o", "bandit-baseline.json"
            ], check=False)
            
            if result.returncode == 0:
                logger.info("✓ Bandit baseline created")
            else:
                logger.warning("Could not create bandit baseline")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create security baseline: {e}")
            return False
    
    def validate_environment(self) -> Dict[str, bool]:
        """Validate the development environment setup."""
        logger.info("Validating development environment...")
        
        validation_results = {}
        
        # Check Python tools
        python_tools = ["black", "isort", "flake8", "mypy", "bandit", "safety", "pre-commit"]
        for tool in python_tools:
            try:
                result = self.run_command([tool, "--version"], check=False)
                validation_results[f"python_{tool}"] = result.returncode == 0
            except FileNotFoundError:
                validation_results[f"python_{tool}"] = False
        
        # Check Node tools
        node_tools = ["eslint", "prettier", "npm"]
        for tool in node_tools:
            try:
                result = self.run_command([tool, "--version"], check=False)
                validation_results[f"node_{tool}"] = result.returncode == 0
            except FileNotFoundError:
                validation_results[f"node_{tool}"] = False
        
        # Check configuration files
        config_files = [
            ".pre-commit-config.yaml",
            ".github/workflows/ci.yml",
            ".github/dependabot.yml",
            "backend/requirements.txt",
            "frontend/package.json"
        ]
        
        for config_file in config_files:
            file_path = self.project_root / config_file
            validation_results[f"config_{config_file.replace('/', '_').replace('.', '_')}"] = file_path.exists()
        
        # Print validation results
        logger.info("\n=== Validation Results ===")
        for check, passed in validation_results.items():
            status = "✓" if passed else "✗"
            logger.info(f"{status} {check}")
        
        return validation_results
    
    def generate_setup_report(self, validation_results: Dict[str, bool]) -> None:
        """Generate a setup report."""
        report = {
            "timestamp": subprocess.run(["date"], capture_output=True, text=True).stdout.strip(),
            "platform": platform.platform(),
            "python_version": sys.version,
            "validation_results": validation_results,
            "total_checks": len(validation_results),
            "passed_checks": sum(validation_results.values()),
            "success_rate": f"{(sum(validation_results.values()) / len(validation_results)) * 100:.1f}%"
        }
        
        report_file = self.project_root / "dev_environment_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Setup report saved to: {report_file}")
        logger.info(f"Success rate: {report['success_rate']}")

def main():
    parser = argparse.ArgumentParser(description="Setup development environment for GLPI Dashboard")
    parser.add_argument("--full", action="store_true", help="Full setup including all tools")
    parser.add_argument("--security-only", action="store_true", help="Install only security tools")
    parser.add_argument("--validate", action="store_true", help="Only validate existing setup")
    parser.add_argument("--project-root", help="Project root directory")
    
    args = parser.parse_args()
    
    setup = DevEnvironmentSetup(args.project_root)
    
    if args.validate:
        validation_results = setup.validate_environment()
        setup.generate_setup_report(validation_results)
        return
    
    logger.info("Starting development environment setup...")
    
    # Check prerequisites
    if not setup.check_prerequisites():
        logger.error("Prerequisites check failed. Please install missing tools.")
        sys.exit(1)
    
    success = True
    
    # Setup Python environment
    if not setup.setup_python_environment(args.security_only):
        success = False
    
    # Setup Node.js environment
    if not setup.setup_node_environment(args.security_only):
        success = False
    
    # Setup pre-commit hooks (unless security-only)
    if not args.security_only:
        if not setup.setup_pre_commit_hooks():
            success = False
    
    # Create security baseline
    if not setup.create_security_baseline():
        success = False
    
    # Validate setup
    validation_results = setup.validate_environment()
    setup.generate_setup_report(validation_results)
    
    if success:
        logger.info("\n🎉 Development environment setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Activate virtual environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)")
        logger.info("2. Run tests: pytest backend/tests/")
        logger.info("3. Start development server: npm run dev (in frontend directory)")
        logger.info("4. Run pre-commit: pre-commit run --all-files")
    else:
        logger.error("\n❌ Some setup steps failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()