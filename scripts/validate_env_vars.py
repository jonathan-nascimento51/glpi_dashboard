#!/usr/bin/env python3
"""Script to validate environment variables configuration."""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Set


class EnvValidator:
    """Validator for environment variables."""
    
    def __init__(self):
        self.required_vars = {
            'GLPI_URL',
            'GLPI_USER_TOKEN',
            'GLPI_APP_TOKEN',
            'DATABASE_URL',
            'SECRET_KEY',
            'ENVIRONMENT'
        }
        
        self.optional_vars = {
            'DEBUG',
            'LOG_LEVEL',
            'CACHE_TTL',
            'API_TIMEOUT',
            'MAX_RETRIES',
            'CORS_ORIGINS',
            'SENTRY_DSN'
        }
        
        self.sensitive_patterns = [
            r'password',
            r'secret',
            r'key',
            r'token',
            r'credential',
            r'auth'
        ]
    
    def validate_env_file(self, file_path: Path) -> List[str]:
        """Validate a single .env file."""
        errors = []
        
        if not file_path.exists():
            errors.append(f"Environment file not found: {file_path}")
            return errors
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            errors.append(f"Error reading {file_path}: {e}")
            return errors
        
        # Parse environment variables
        env_vars = self._parse_env_content(content)
        
        # Validate format
        errors.extend(self._validate_format(content, file_path))
        
        # Validate required variables (only for .env, not .env.example)
        if not file_path.name.endswith('.example'):
            errors.extend(self._validate_required_vars(env_vars, file_path))
        
        # Validate variable values
        errors.extend(self._validate_values(env_vars, file_path))
        
        # Check for sensitive data in .env.example
        if file_path.name.endswith('.example'):
            errors.extend(self._check_sensitive_data(env_vars, file_path))
        
        return errors
    
    def _parse_env_content(self, content: str) -> Dict[str, str]:
        """Parse environment variables from content."""
        env_vars = {}
        
        for line_num, line in enumerate(content.splitlines(), 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                env_vars[key] = value
        
        return env_vars
    
    def _validate_format(self, content: str, file_path: Path) -> List[str]:
        """Validate the format of the environment file."""
        errors = []
        
        for line_num, line in enumerate(content.splitlines(), 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Check for proper KEY=VALUE format
            if '=' not in line:
                errors.append(
                    f"{file_path}:{line_num}: Invalid format. "
                    f"Expected KEY=VALUE, got: {line}"
                )
                continue
            
            key, value = line.split('=', 1)
            key = key.strip()
            
            # Validate key format
            if not re.match(r'^[A-Z][A-Z0-9_]*$', key):
                errors.append(
                    f"{file_path}:{line_num}: Invalid key format. "
                    f"Keys should be UPPERCASE_WITH_UNDERSCORES: {key}"
                )
            
            # Check for spaces around =
            if line.count('=') > 1 and '=' in value:
                # Multiple = signs, check if it's intentional (like in URLs)
                if not any(pattern in value.lower() for pattern in ['http', 'postgresql', 'mysql']):
                    errors.append(
                        f"{file_path}:{line_num}: Multiple '=' signs detected. "
                        f"Consider quoting the value: {line}"
                    )
        
        return errors
    
    def _validate_required_vars(self, env_vars: Dict[str, str], file_path: Path) -> List[str]:
        """Validate that all required variables are present."""
        errors = []
        missing_vars = self.required_vars - set(env_vars.keys())
        
        if missing_vars:
            errors.append(
                f"{file_path}: Missing required environment variables: "
                f"{', '.join(sorted(missing_vars))}"
            )
        
        return errors
    
    def _validate_values(self, env_vars: Dict[str, str], file_path: Path) -> List[str]:
        """Validate the values of environment variables."""
        errors = []
        
        for key, value in env_vars.items():
            # Check for empty values in required variables
            if key in self.required_vars and not value:
                errors.append(
                    f"{file_path}: Required variable {key} cannot be empty"
                )
            
            # Validate specific variable formats
            if key == 'GLPI_URL':
                if value and not re.match(r'^https?://.+', value):
                    errors.append(
                        f"{file_path}: GLPI_URL must be a valid HTTP/HTTPS URL: {value}"
                    )
            
            elif key == 'DATABASE_URL':
                if value and not re.match(r'^(postgresql|mysql|sqlite)://.+', value):
                    errors.append(
                        f"{file_path}: DATABASE_URL must be a valid database URL: {value}"
                    )
            
            elif key == 'ENVIRONMENT':
                valid_envs = {'development', 'staging', 'production', 'test'}
                if value and value.lower() not in valid_envs:
                    errors.append(
                        f"{file_path}: ENVIRONMENT must be one of {valid_envs}: {value}"
                    )
            
            elif key == 'DEBUG':
                if value and value.lower() not in {'true', 'false', '1', '0'}:
                    errors.append(
                        f"{file_path}: DEBUG must be true/false or 1/0: {value}"
                    )
            
            elif key == 'LOG_LEVEL':
                valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
                if value and value.upper() not in valid_levels:
                    errors.append(
                        f"{file_path}: LOG_LEVEL must be one of {valid_levels}: {value}"
                    )
            
            elif key in {'CACHE_TTL', 'API_TIMEOUT', 'MAX_RETRIES'}:
                if value and not value.isdigit():
                    errors.append(
                        f"{file_path}: {key} must be a positive integer: {value}"
                    )
        
        return errors
    
    def _check_sensitive_data(self, env_vars: Dict[str, str], file_path: Path) -> List[str]:
        """Check for sensitive data in .env.example files."""
        errors = []
        
        for key, value in env_vars.items():
            # Check if key suggests sensitive data
            key_lower = key.lower()
            is_sensitive = any(pattern in key_lower for pattern in self.sensitive_patterns)
            
            if is_sensitive and value and value != 'your_value_here':
                # Check if value looks like real sensitive data
                if len(value) > 10 and not value.startswith('your_') and not value.startswith('example_'):
                    errors.append(
                        f"{file_path}: Potential sensitive data in example file. "
                        f"Variable {key} should use placeholder value: {value}"
                    )
        
        return errors
    
    def validate_consistency(self, env_file: Path, example_file: Path) -> List[str]:
        """Validate consistency between .env and .env.example files."""
        errors = []
        
        if not example_file.exists():
            return [f"Example file not found: {example_file}"]
        
        try:
            env_content = env_file.read_text(encoding='utf-8') if env_file.exists() else ''
            example_content = example_file.read_text(encoding='utf-8')
            
            env_vars = set(self._parse_env_content(env_content).keys())
            example_vars = set(self._parse_env_content(example_content).keys())
            
            # Check for variables in .env but not in .env.example
            missing_in_example = env_vars - example_vars
            if missing_in_example:
                errors.append(
                    f"Variables in {env_file.name} but not in {example_file.name}: "
                    f"{', '.join(sorted(missing_in_example))}"
                )
            
            # Check for required variables missing from .env.example
            missing_required = self.required_vars - example_vars
            if missing_required:
                errors.append(
                    f"Required variables missing from {example_file.name}: "
                    f"{', '.join(sorted(missing_required))}"
                )
        
        except Exception as e:
            errors.append(f"Error comparing files: {e}")
        
        return errors


def main():
    """Main function to validate environment files."""
    validator = EnvValidator()
    project_root = Path(__file__).parent.parent
    
    # Files to validate
    env_files = [
        project_root / '.env',
        project_root / '.env.example',
        project_root / 'backend' / '.env',
        project_root / 'backend' / '.env.example',
        project_root / 'frontend' / '.env',
        project_root / 'frontend' / '.env.example'
    ]
    
    all_errors = []
    
    # Validate individual files
    for env_file in env_files:
        if env_file.exists():
            print(f"Validating {env_file}...")
            errors = validator.validate_env_file(env_file)
            all_errors.extend(errors)
    
    # Validate consistency between .env and .env.example
    consistency_pairs = [
        (project_root / '.env', project_root / '.env.example'),
        (project_root / 'backend' / '.env', project_root / 'backend' / '.env.example'),
        (project_root / 'frontend' / '.env', project_root / 'frontend' / '.env.example')
    ]
    
    for env_file, example_file in consistency_pairs:
        if example_file.exists():
            print(f"Checking consistency between {env_file.name} and {example_file.name}...")
            errors = validator.validate_consistency(env_file, example_file)
            all_errors.extend(errors)
    
    # Report results
    if all_errors:
        print("\n❌ Environment validation failed:")
        for error in all_errors:
            print(f"  • {error}")
        sys.exit(1)
    else:
        print("\n✅ All environment files are valid!")
        sys.exit(0)


if __name__ == '__main__':
    main()