import re
import os
from collections import Counter
from datetime import datetime

class LinuxLogAnalyzer:
    # Change the default path to the standard Linux syslog
    def __init__(self, log_path="/var/log/syslog"):
        self.log_path = log_path
        # Define keywords to capture, covering common hardware and system errors
        self.error_patterns = [
            re.compile(r"error", re.IGNORECASE),
            re.compile(r"fail", re.IGNORECASE),
            re.compile(r"warning", re.IGNORECASE),
            re.compile(r"thermal", re.IGNORECASE),  # Thermal warning
            re.compile(r"hardware", re.IGNORECASE), # Hardware level events
            re.compile(r"kernel", re.IGNORECASE)    # Kernel crash or warning
        ]
        self.found_errors = []
        
    def analyze_recent_logs(self):
        """Read Linux system logs and extract errors"""
        if not os.path.exists(self.log_path):
            return {"status": f"Log file not found: {self.log_path}", "data": []}

        try:
            with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Read the last 500 lines
            recent_lines = lines[-500:] 
            
            for line in recent_lines:
                for pattern in self.error_patterns:
                    if pattern.search(line):
                        self.found_errors.append(line.strip())
                        break
                        
            return self._generate_summary()
            
        except Exception as e:
            return {"status": f"Error reading log: {e}", "data": []}

    def _generate_summary(self):
        """Count error types and generate a summary"""
        error_counts = Counter()
        for log in self.found_errors:
            for pattern in self.error_patterns:
                if pattern.search(log):
                    error_counts[pattern.pattern] += 1

        return {
            "status": "Success",
            "total_errors_found": len(self.found_errors),
            "summary": dict(error_counts),
            "raw_logs": self.found_errors[-10:] # The latest 10 entries
        }
