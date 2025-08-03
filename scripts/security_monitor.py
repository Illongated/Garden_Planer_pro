#!/usr/bin/env python3
"""
Security Monitoring Script for Agrotique Garden Planner
Comprehensive security monitoring and alerting system.
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiohttp
import psutil
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/security/logs/security_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SecurityMonitor:
    """Comprehensive security monitoring system."""
    
    def __init__(self, config_path: str = "/app/security/config.yaml"):
        self.config = self.load_config(config_path)
        self.alerts: List[Dict] = []
        self.last_check = datetime.now()
        
    def load_config(self, config_path: str) -> Dict:
        """Load security configuration."""
        default_config = {
            "monitoring": {
                "check_interval": 300,  # 5 minutes
                "alert_threshold": 10,
                "log_retention_days": 30
            },
            "checks": {
                "file_integrity": True,
                "process_monitoring": True,
                "network_monitoring": True,
                "log_analysis": True,
                "vulnerability_scan": True
            },
            "alerts": {
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "recipients": []
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "headers": {}
                }
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    return {**default_config, **config}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
        
        return default_config
    
    async def run_security_checks(self) -> Dict[str, List[str]]:
        """Run all security checks."""
        results = {
            "warnings": [],
            "errors": [],
            "alerts": []
        }
        
        try:
            # File integrity check
            if self.config["checks"]["file_integrity"]:
                file_issues = await self.check_file_integrity()
                results["warnings"].extend(file_issues)
            
            # Process monitoring
            if self.config["checks"]["process_monitoring"]:
                process_issues = await self.check_processes()
                results["warnings"].extend(process_issues)
            
            # Network monitoring
            if self.config["checks"]["network_monitoring"]:
                network_issues = await self.check_network()
                results["warnings"].extend(network_issues)
            
            # Log analysis
            if self.config["checks"]["log_analysis"]:
                log_issues = await self.analyze_logs()
                results["alerts"].extend(log_issues)
            
            # Vulnerability scan
            if self.config["checks"]["vulnerability_scan"]:
                vuln_issues = await self.scan_vulnerabilities()
                results["errors"].extend(vuln_issues)
            
        except Exception as e:
            logger.error(f"Error during security checks: {e}")
            results["errors"].append(f"Security check error: {e}")
        
        return results
    
    async def check_file_integrity(self) -> List[str]:
        """Check file integrity and permissions."""
        issues = []
        
        critical_files = [
            "/app/app/main.py",
            "/app/app/core/security.py",
            "/app/requirements.txt",
            "/app/alembic.ini"
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                # Check file permissions
                stat = os.stat(file_path)
                if stat.st_mode & 0o777 != 0o644:
                    issues.append(f"Insecure permissions on {file_path}: {oct(stat.st_mode)}")
                
                # Check file ownership
                if stat.st_uid == 0:
                    issues.append(f"File owned by root: {file_path}")
            else:
                issues.append(f"Critical file missing: {file_path}")
        
        # Check for suspicious files
        suspicious_patterns = [
            r"\.pyc$",
            r"\.log$",
            r"\.tmp$",
            r"\.bak$"
        ]
        
        for root, dirs, files in os.walk("/app"):
            for file in files:
                file_path = os.path.join(root, file)
                for pattern in suspicious_patterns:
                    if re.search(pattern, file_path):
                        issues.append(f"Suspicious file found: {file_path}")
        
        return issues
    
    async def check_processes(self) -> List[str]:
        """Monitor running processes for suspicious activity."""
        issues = []
        
        try:
            # Check for unexpected processes
            expected_processes = [
                "python", "uvicorn", "nginx", "redis-server", "postgres"
            ]
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    
                    # Check for unexpected processes
                    if proc_name not in expected_processes:
                        issues.append(f"Unexpected process: {proc_name} (PID: {proc_info['pid']})")
                    
                    # Check for processes with high CPU usage
                    if proc.cpu_percent() > 80:
                        issues.append(f"High CPU usage: {proc_name} ({proc.cpu_percent()}%)")
                    
                    # Check for processes with high memory usage
                    if proc.memory_percent() > 80:
                        issues.append(f"High memory usage: {proc_name} ({proc.memory_percent()}%)")
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            issues.append(f"Process monitoring error: {e}")
        
        return issues
    
    async def check_network(self) -> List[str]:
        """Monitor network connections."""
        issues = []
        
        try:
            # Check for unexpected network connections
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED':
                    # Check for connections to suspicious IPs
                    if conn.raddr and conn.raddr.ip:
                        ip = conn.raddr.ip
                        if not self.is_trusted_ip(ip):
                            issues.append(f"Connection to untrusted IP: {ip}:{conn.raddr.port}")
            
            # Check for listening ports
            listening_ports = []
            for conn in psutil.net_connections():
                if conn.status == 'LISTEN':
                    listening_ports.append(conn.laddr.port)
            
            expected_ports = [8000, 80, 443, 5432, 6379]
            for port in listening_ports:
                if port not in expected_ports:
                    issues.append(f"Unexpected listening port: {port}")
                    
        except Exception as e:
            issues.append(f"Network monitoring error: {e}")
        
        return issues
    
    def is_trusted_ip(self, ip: str) -> bool:
        """Check if IP is trusted."""
        trusted_ranges = [
            "127.0.0.1",
            "10.0.0.0/8",
            "172.16.0.0/12",
            "192.168.0.0/16"
        ]
        
        # Simple check for localhost
        if ip == "127.0.0.1":
            return True
        
        # Check private IP ranges
        ip_parts = ip.split('.')
        if len(ip_parts) == 4:
            first_octet = int(ip_parts[0])
            if first_octet == 10 or (172 <= first_octet <= 191) or (192 <= first_octet <= 223):
                return True
        
        return False
    
    async def analyze_logs(self) -> List[str]:
        """Analyze logs for security issues."""
        alerts = []
        
        log_files = [
            "/app/security/logs/security_monitor.log",
            "/var/log/nginx/access.log",
            "/var/log/nginx/error.log"
        ]
        
        suspicious_patterns = [
            r"sqlmap",
            r"nikto",
            r"nmap",
            r"admin.*login",
            r"password.*reset",
            r"failed.*login",
            r"rate.*limit",
            r"blocked.*ip",
            r"xss.*attempt",
            r"csrf.*violation"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        
                        for line in lines:
                            for pattern in suspicious_patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    alerts.append(f"Suspicious activity in {log_file}: {line.strip()}")
                                    
                except Exception as e:
                    alerts.append(f"Error reading log file {log_file}: {e}")
        
        return alerts
    
    async def scan_vulnerabilities(self) -> List[str]:
        """Scan for common vulnerabilities."""
        issues = []
        
        try:
            # Check for outdated packages
            result = subprocess.run(
                ["pip", "list", "--outdated"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                outdated_packages = result.stdout.strip().split('\n')[2:]  # Skip header
                if outdated_packages:
                    issues.append(f"Outdated packages found: {len(outdated_packages)}")
            
            # Check for known vulnerabilities
            result = subprocess.run(
                ["safety", "check"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0 and result.stderr:
                issues.append(f"Vulnerability scan issues: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            issues.append("Vulnerability scan timed out")
        except Exception as e:
            issues.append(f"Vulnerability scan error: {e}")
        
        return issues
    
    async def send_alerts(self, alerts: List[str]):
        """Send security alerts."""
        if not alerts:
            return
        
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "alerts": alerts,
            "severity": "high" if len(alerts) > 5 else "medium"
        }
        
        # Send to webhook if configured
        if self.config["alerts"]["webhook"]["enabled"]:
            await self.send_webhook_alert(alert_data)
        
        # Send email if configured
        if self.config["alerts"]["email"]["enabled"]:
            await self.send_email_alert(alert_data)
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"SECURITY ALERT: {alert}")
    
    async def send_webhook_alert(self, alert_data: Dict):
        """Send alert to webhook."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config["alerts"]["webhook"]["url"],
                    json=alert_data,
                    headers=self.config["alerts"]["webhook"]["headers"]
                ) as response:
                    if response.status != 200:
                        logger.error(f"Webhook alert failed: {response.status}")
        except Exception as e:
            logger.error(f"Webhook alert error: {e}")
    
    async def send_email_alert(self, alert_data: Dict):
        """Send alert via email."""
        # Implementation would depend on email service
        logger.info("Email alert would be sent here")
    
    async def cleanup_old_logs(self):
        """Clean up old log files."""
        try:
            retention_days = self.config["monitoring"]["log_retention_days"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            log_dir = Path("/app/security/logs")
            if log_dir.exists():
                for log_file in log_dir.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        log_file.unlink()
                        logger.info(f"Deleted old log file: {log_file}")
                        
        except Exception as e:
            logger.error(f"Log cleanup error: {e}")
    
    async def run_monitoring_loop(self):
        """Main monitoring loop."""
        logger.info("Starting security monitoring...")
        
        while True:
            try:
                # Run security checks
                results = await self.run_security_checks()
                
                # Process results
                all_alerts = results["warnings"] + results["errors"] + results["alerts"]
                
                if all_alerts:
                    await self.send_alerts(all_alerts)
                
                # Log summary
                logger.info(f"Security check completed: {len(results['warnings'])} warnings, "
                          f"{len(results['errors'])} errors, {len(results['alerts'])} alerts")
                
                # Cleanup old logs
                await self.cleanup_old_logs()
                
                # Wait for next check
                await asyncio.sleep(self.config["monitoring"]["check_interval"])
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

async def main():
    """Main function."""
    monitor = SecurityMonitor()
    await monitor.run_monitoring_loop()

if __name__ == "__main__":
    asyncio.run(main()) 