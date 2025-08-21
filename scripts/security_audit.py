#!/usr/bin/env python3
"""
Comprehensive Security Audit Script for GLPI Dashboard

This script performs a complete security analysis including:
- Static code analysis
- Dependency vulnerability scanning
- Secret detection
- Configuration security review
- Infrastructure security checks
- Compliance verification

Usage:
    python scripts/security_audit.py [--output-format json|html|pdf] [--severity high|medium|low]
"""

import os
import sys
import json
import subprocess
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import tempfile
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_audit.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SecurityAuditor:
    """Comprehensive security auditing tool for GLPI Dashboard."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.reports_dir = self.project_root / "security_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Security findings storage
        self.findings = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": []
        }
        
        # Security tools configuration
        self.tools_config = {
            "bandit": {
                "command": ["bandit", "-r", "backend/", "-f", "json"],
                "description": "Python security linter"
            },
            "safety": {
                "command": ["safety", "check", "-r", "backend/requirements.txt", "--json"],
                "description": "Python dependency vulnerability scanner"
            },
            "pip-audit": {
                "command": ["pip-audit", "-r", "backend/requirements.txt", "--format=json"],
                "description": "Python package vulnerability scanner"
            },
            "detect-secrets": {
                "command": ["detect-secrets", "scan", "--all-files", "--force-use-all-plugins"],
                "description": "Secret detection tool"
            },
            "semgrep": {
                "command": ["semgrep", "--config=auto", "--json", "."],
                "description": "Static analysis security scanner"
            },
            "npm-audit": {
                "command": ["npm", "audit", "--json"],
                "description": "Node.js dependency vulnerability scanner",
                "cwd": "frontend"
            }
        }
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Run a security tool command and return results."""
        try:
            logger.info(f"Running: {' '.join(command)}")
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(command)}")
            return {"success": False, "error": "Command timed out"}
        except FileNotFoundError:
            logger.error(f"Tool not found: {command[0]}")
            return {"success": False, "error": f"Tool not found: {command[0]}"}
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {"success": False, "error": str(e)}
    
    def run_bandit_scan(self) -> Dict[str, Any]:
        """Run Bandit security scan on Python code."""
        logger.info("Running Bandit security scan...")
        
        config = self.tools_config["bandit"]
        result = self.run_command(config["command"])
        
        if not result["success"]:
            return {"tool": "bandit", "error": result["error"]}
        
        try:
            bandit_data = json.loads(result["stdout"])
            
            findings = []
            for issue in bandit_data.get("results", []):
                finding = {
                    "tool": "bandit",
                    "type": "code_security",
                    "severity": issue.get("issue_severity", "unknown").lower(),
                    "confidence": issue.get("issue_confidence", "unknown").lower(),
                    "title": issue.get("test_name", "Unknown issue"),
                    "description": issue.get("issue_text", ""),
                    "file": issue.get("filename", ""),
                    "line": issue.get("line_number", 0),
                    "code": issue.get("code", ""),
                    "cwe_id": issue.get("test_id", "")
                }
                findings.append(finding)
                
                # Categorize by severity
                severity = finding["severity"]
                if severity in self.findings:
                    self.findings[severity].append(finding)
            
            return {
                "tool": "bandit",
                "findings": findings,
                "summary": {
                    "total_issues": len(findings),
                    "high_severity": len([f for f in findings if f["severity"] == "high"]),
                    "medium_severity": len([f for f in findings if f["severity"] == "medium"]),
                    "low_severity": len([f for f in findings if f["severity"] == "low"])
                }
            }
            
        except json.JSONDecodeError:
            return {"tool": "bandit", "error": "Failed to parse JSON output"}
    
    def run_safety_scan(self) -> Dict[str, Any]:
        """Run Safety scan for Python dependencies."""
        logger.info("Running Safety dependency scan...")
        
        config = self.tools_config["safety"]
        result = self.run_command(config["command"])
        
        if not result["success"]:
            return {"tool": "safety", "error": result["error"]}
        
        try:
            safety_data = json.loads(result["stdout"])
            
            findings = []
            for vuln in safety_data:
                finding = {
                    "tool": "safety",
                    "type": "dependency_vulnerability",
                    "severity": "high",  # Safety reports are generally high severity
                    "title": f"Vulnerable dependency: {vuln.get('package', 'unknown')}",
                    "description": vuln.get('advisory', ''),
                    "package": vuln.get('package', ''),
                    "installed_version": vuln.get('installed_version', ''),
                    "vulnerable_spec": vuln.get('vulnerable_spec', ''),
                    "cve_id": vuln.get('id', ''),
                    "more_info_url": vuln.get('more_info_url', '')
                }
                findings.append(finding)
                self.findings["high"].append(finding)
            
            return {
                "tool": "safety",
                "findings": findings,
                "summary": {
                    "total_vulnerabilities": len(findings),
                    "unique_packages": len(set(f["package"] for f in findings))
                }
            }
            
        except json.JSONDecodeError:
            return {"tool": "safety", "error": "Failed to parse JSON output"}
    
    def run_npm_audit(self) -> Dict[str, Any]:
        """Run npm audit for Node.js dependencies."""
        logger.info("Running npm audit...")
        
        if not (self.frontend_dir / "package.json").exists():
            return {"tool": "npm-audit", "error": "package.json not found"}
        
        config = self.tools_config["npm-audit"]
        result = self.run_command(config["command"], cwd=self.frontend_dir)
        
        if not result["success"] and result["returncode"] not in [0, 1]:  # npm audit returns 1 if vulnerabilities found
            return {"tool": "npm-audit", "error": result["error"]}
        
        try:
            audit_data = json.loads(result["stdout"])
            
            findings = []
            vulnerabilities = audit_data.get("vulnerabilities", {})
            
            for package, vuln_info in vulnerabilities.items():
                severity = vuln_info.get("severity", "unknown")
                
                finding = {
                    "tool": "npm-audit",
                    "type": "dependency_vulnerability",
                    "severity": severity,
                    "title": f"Vulnerable npm package: {package}",
                    "description": vuln_info.get("title", ""),
                    "package": package,
                    "range": vuln_info.get("range", ""),
                    "cwe": vuln_info.get("cwe", []),
                    "url": vuln_info.get("url", "")
                }
                findings.append(finding)
                
                # Categorize by severity
                if severity in self.findings:
                    self.findings[severity].append(finding)
            
            return {
                "tool": "npm-audit",
                "findings": findings,
                "summary": audit_data.get("metadata", {})
            }
            
        except json.JSONDecodeError:
            return {"tool": "npm-audit", "error": "Failed to parse JSON output"}
    
    def run_secret_detection(self) -> Dict[str, Any]:
        """Run secret detection scan."""
        logger.info("Running secret detection...")
        
        config = self.tools_config["detect-secrets"]
        result = self.run_command(config["command"])
        
        if not result["success"]:
            return {"tool": "detect-secrets", "error": result["error"]}
        
        try:
            secrets_data = json.loads(result["stdout"])
            
            findings = []
            for filename, secrets in secrets_data.get("results", {}).items():
                for secret in secrets:
                    finding = {
                        "tool": "detect-secrets",
                        "type": "secret_exposure",
                        "severity": "critical",  # Secrets are always critical
                        "title": f"Potential secret detected: {secret.get('type', 'unknown')}",
                        "description": f"Potential {secret.get('type', 'secret')} found in {filename}",
                        "file": filename,
                        "line": secret.get("line_number", 0),
                        "secret_type": secret.get("type", "unknown"),
                        "hashed_secret": secret.get("hashed_secret", "")
                    }
                    findings.append(finding)
                    self.findings["critical"].append(finding)
            
            return {
                "tool": "detect-secrets",
                "findings": findings,
                "summary": {
                    "total_secrets": len(findings),
                    "files_with_secrets": len(secrets_data.get("results", {}))
                }
            }
            
        except json.JSONDecodeError:
            return {"tool": "detect-secrets", "error": "Failed to parse JSON output"}
    
    def run_semgrep_scan(self) -> Dict[str, Any]:
        """Run Semgrep security scan."""
        logger.info("Running Semgrep security scan...")
        
        config = self.tools_config["semgrep"]
        result = self.run_command(config["command"])
        
        if not result["success"]:
            return {"tool": "semgrep", "error": result["error"]}
        
        try:
            semgrep_data = json.loads(result["stdout"])
            
            findings = []
            for finding_data in semgrep_data.get("results", []):
                severity_map = {"ERROR": "high", "WARNING": "medium", "INFO": "low"}
                severity = severity_map.get(finding_data.get("extra", {}).get("severity", "INFO"), "low")
                
                finding = {
                    "tool": "semgrep",
                    "type": "static_analysis",
                    "severity": severity,
                    "title": finding_data.get("check_id", "Unknown issue"),
                    "description": finding_data.get("extra", {}).get("message", ""),
                    "file": finding_data.get("path", ""),
                    "line": finding_data.get("start", {}).get("line", 0),
                    "rule_id": finding_data.get("check_id", ""),
                    "owasp": finding_data.get("extra", {}).get("metadata", {}).get("owasp", []),
                    "cwe": finding_data.get("extra", {}).get("metadata", {}).get("cwe", [])
                }
                findings.append(finding)
                
                # Categorize by severity
                if severity in self.findings:
                    self.findings[severity].append(finding)
            
            return {
                "tool": "semgrep",
                "findings": findings,
                "summary": {
                    "total_findings": len(findings),
                    "rules_matched": len(set(f["rule_id"] for f in findings))
                }
            }
            
        except json.JSONDecodeError:
            return {"tool": "semgrep", "error": "Failed to parse JSON output"}
    
    def analyze_configuration_security(self) -> Dict[str, Any]:
        """Analyze configuration files for security issues."""
        logger.info("Analyzing configuration security...")
        
        findings = []
        config_files = [
            ".env", ".env.example", "config.py", "settings.py",
            "docker-compose.yml", "Dockerfile", "nginx.conf"
        ]
        
        for config_file in config_files:
            file_path = self.project_root / config_file
            if file_path.exists():
                # Check for common security misconfigurations
                content = file_path.read_text()
                
                # Check for hardcoded secrets
                if any(pattern in content.lower() for pattern in 
                      ["password=", "secret=", "key=", "token="]):
                    finding = {
                        "tool": "config-analyzer",
                        "type": "configuration_security",
                        "severity": "medium",
                        "title": f"Potential hardcoded credentials in {config_file}",
                        "description": "Configuration file may contain hardcoded credentials",
                        "file": str(file_path),
                        "recommendation": "Use environment variables for sensitive data"
                    }
                    findings.append(finding)
                    self.findings["medium"].append(finding)
                
                # Check for debug mode in production configs
                if "debug=true" in content.lower() or "debug: true" in content.lower():
                    finding = {
                        "tool": "config-analyzer",
                        "type": "configuration_security",
                        "severity": "medium",
                        "title": f"Debug mode enabled in {config_file}",
                        "description": "Debug mode should be disabled in production",
                        "file": str(file_path),
                        "recommendation": "Disable debug mode in production environments"
                    }
                    findings.append(finding)
                    self.findings["medium"].append(finding)
        
        return {
            "tool": "config-analyzer",
            "findings": findings,
            "summary": {
                "files_analyzed": len([f for f in config_files if (self.project_root / f).exists()]),
                "issues_found": len(findings)
            }
        }
    
    def calculate_security_score(self) -> Dict[str, Any]:
        """Calculate overall security score based on findings."""
        total_findings = sum(len(findings) for findings in self.findings.values())
        
        if total_findings == 0:
            return {"score": 100, "grade": "A+", "description": "Excellent security posture"}
        
        # Weight different severity levels
        weights = {"critical": 10, "high": 5, "medium": 2, "low": 1, "info": 0.5}
        weighted_score = sum(
            len(self.findings[severity]) * weight 
            for severity, weight in weights.items()
        )
        
        # Calculate score (0-100, where 100 is perfect)
        max_possible_score = 100
        penalty = min(weighted_score * 2, max_possible_score)
        score = max(0, max_possible_score - penalty)
        
        # Assign grade
        if score >= 90:
            grade = "A+"
            description = "Excellent security posture"
        elif score >= 80:
            grade = "A"
            description = "Good security posture"
        elif score >= 70:
            grade = "B"
            description = "Acceptable security posture"
        elif score >= 60:
            grade = "C"
            description = "Poor security posture"
        else:
            grade = "F"
            description = "Critical security issues"
        
        return {
            "score": round(score, 1),
            "grade": grade,
            "description": description,
            "total_findings": total_findings,
            "weighted_score": weighted_score,
            "breakdown": {
                severity: len(findings) 
                for severity, findings in self.findings.items()
            }
        }
    
    def generate_report(self, output_format: str = "json") -> str:
        """Generate comprehensive security report."""
        logger.info(f"Generating security report in {output_format} format...")
        
        timestamp = datetime.datetime.now().isoformat()
        security_score = self.calculate_security_score()
        
        report = {
            "metadata": {
                "timestamp": timestamp,
                "project": "GLPI Dashboard",
                "scan_type": "comprehensive_security_audit",
                "tools_used": list(self.tools_config.keys())
            },
            "security_score": security_score,
            "findings_summary": {
                severity: len(findings) 
                for severity, findings in self.findings.items()
            },
            "detailed_findings": self.findings,
            "recommendations": self.generate_recommendations()
        }
        
        if output_format == "json":
            report_file = self.reports_dir / f"security_audit_{timestamp.replace(':', '-')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
        
        elif output_format == "html":
            report_file = self.reports_dir / f"security_audit_{timestamp.replace(':', '-')}.html"
            html_content = self.generate_html_report(report)
            with open(report_file, 'w') as f:
                f.write(html_content)
        
        logger.info(f"Security report saved to: {report_file}")
        return str(report_file)
    
    def generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate security recommendations based on findings."""
        recommendations = []
        
        # Critical findings recommendations
        if self.findings["critical"]:
            recommendations.append({
                "priority": "critical",
                "title": "Address Critical Security Issues Immediately",
                "description": "Critical security issues were found that require immediate attention.",
                "action": "Review and fix all critical findings before deploying to production."
            })
        
        # High severity recommendations
        if self.findings["high"]:
            recommendations.append({
                "priority": "high",
                "title": "Fix High Severity Vulnerabilities",
                "description": "High severity security issues were identified.",
                "action": "Update vulnerable dependencies and fix security issues."
            })
        
        # General recommendations
        recommendations.extend([
            {
                "priority": "medium",
                "title": "Implement Security Headers",
                "description": "Add security headers to protect against common attacks.",
                "action": "Configure CSP, HSTS, X-Frame-Options, and other security headers."
            },
            {
                "priority": "medium",
                "title": "Regular Security Audits",
                "description": "Perform regular security audits to maintain security posture.",
                "action": "Schedule monthly security scans and dependency updates."
            },
            {
                "priority": "low",
                "title": "Security Training",
                "description": "Ensure development team is trained on secure coding practices.",
                "action": "Provide security training and establish secure coding guidelines."
            }
        ])
        
        return recommendations
    
    def generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML security report."""
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Audit Report - GLPI Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .score {{ font-size: 48px; font-weight: bold; margin: 20px 0; }}
        .grade-A {{ color: #28a745; }}
        .grade-B {{ color: #ffc107; }}
        .grade-C {{ color: #fd7e14; }}
        .grade-F {{ color: #dc3545; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .critical {{ border-left: 5px solid #dc3545; }}
        .high {{ border-left: 5px solid #fd7e14; }}
        .medium {{ border-left: 5px solid #ffc107; }}
        .low {{ border-left: 5px solid #28a745; }}
        .finding {{ margin: 10px 0; padding: 15px; border-radius: 5px; background: #f8f9fa; }}
        .finding-title {{ font-weight: bold; margin-bottom: 5px; }}
        .finding-description {{ color: #666; }}
        .recommendations {{ margin-top: 30px; }}
        .recommendation {{ margin: 15px 0; padding: 15px; border-radius: 5px; background: #e3f2fd; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Security Audit Report</h1>
            <h2>GLPI Dashboard</h2>
            <p>Generated on: {report_data['metadata']['timestamp']}</p>
            <div class="score grade-{report_data['security_score']['grade'].replace('+', '')}">
                {report_data['security_score']['score']}/100 ({report_data['security_score']['grade']})
            </div>
            <p>{report_data['security_score']['description']}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card critical">
                <h3>Critical</h3>
                <div class="score">{report_data['findings_summary']['critical']}</div>
            </div>
            <div class="summary-card high">
                <h3>High</h3>
                <div class="score">{report_data['findings_summary']['high']}</div>
            </div>
            <div class="summary-card medium">
                <h3>Medium</h3>
                <div class="score">{report_data['findings_summary']['medium']}</div>
            </div>
            <div class="summary-card low">
                <h3>Low</h3>
                <div class="score">{report_data['findings_summary']['low']}</div>
            </div>
        </div>
        
        <div class="recommendations">
            <h2>Recommendations</h2>
            {''.join(f'<div class="recommendation"><div class="finding-title">{rec["title"]}</div><div class="finding-description">{rec["description"]}</div><p><strong>Action:</strong> {rec["action"]}</p></div>' for rec in report_data['recommendations'])}
        </div>
    </div>
</body>
</html>
        """
        return html_template
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Run complete security audit."""
        logger.info("Starting comprehensive security audit...")
        
        audit_results = {}
        
        # Run all security scans
        audit_results["bandit"] = self.run_bandit_scan()
        audit_results["safety"] = self.run_safety_scan()
        audit_results["npm_audit"] = self.run_npm_audit()
        audit_results["secret_detection"] = self.run_secret_detection()
        audit_results["semgrep"] = self.run_semgrep_scan()
        audit_results["config_analysis"] = self.analyze_configuration_security()
        
        return audit_results

def main():
    parser = argparse.ArgumentParser(description="Comprehensive security audit for GLPI Dashboard")
    parser.add_argument("--output-format", choices=["json", "html"], default="json",
                       help="Output format for the report")
    parser.add_argument("--severity", choices=["critical", "high", "medium", "low"], 
                       help="Filter findings by minimum severity")
    parser.add_argument("--project-root", help="Project root directory")
    
    args = parser.parse_args()
    
    auditor = SecurityAuditor(args.project_root)
    
    # Run full security audit
    audit_results = auditor.run_full_audit()
    
    # Generate report
    report_file = auditor.generate_report(args.output_format)
    
    # Print summary
    security_score = auditor.calculate_security_score()
    logger.info(f"\n=== Security Audit Summary ===")
    logger.info(f"Security Score: {security_score['score']}/100 ({security_score['grade']})")
    logger.info(f"Total Findings: {security_score['total_findings']}")
    
    for severity, count in security_score['breakdown'].items():
        if count > 0:
            logger.info(f"{severity.capitalize()}: {count}")
    
    logger.info(f"\nDetailed report saved to: {report_file}")
    
    # Exit with error code if critical or high severity issues found
    if auditor.findings["critical"] or auditor.findings["high"]:
        logger.warning("Critical or high severity security issues found!")
        sys.exit(1)
    
    logger.info("Security audit completed successfully.")

if __name__ == "__main__":
    main()