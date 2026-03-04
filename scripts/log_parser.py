import re
import os
from collections import Counter
from datetime import datetime

class LinuxLogAnalyzer:
    # 將預設路徑改為 Linux 系統標準的 syslog
    def __init__(self, log_path="/var/log/syslog"):
        self.log_path = log_path
        # 定義要捕捉的關鍵字，涵蓋硬體與系統常見錯誤
        self.error_patterns = [
            re.compile(r"error", re.IGNORECASE),
            re.compile(r"fail", re.IGNORECASE),
            re.compile(r"warning", re.IGNORECASE),
            re.compile(r"thermal", re.IGNORECASE), # 散熱警告
            re.compile(r"hardware", re.IGNORECASE), # 硬體層級事件
            re.compile(r"kernel", re.IGNORECASE)    # 核心崩潰或警告
        ]
        self.found_errors = []
        
    def analyze_recent_logs(self):
        """讀取 Linux 系統日誌並抓取錯誤"""
        if not os.path.exists(self.log_path):
            return {"status": f"找不到日誌檔案: {self.log_path}", "data": []}

        try:
            with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # 讀取最後 500 行
            recent_lines = lines[-500:] 
            
            for line in recent_lines:
                for pattern in self.error_patterns:
                    if pattern.search(line):
                        self.found_errors.append(line.strip())
                        break
                        
            return self._generate_summary()
            
        except Exception as e:
            return {"status": f"讀取日誌發生錯誤: {e}", "data": []}

    def _generate_summary(self):
        """統計錯誤類型並生成摘要"""
        error_counts = Counter()
        for log in self.found_errors:
            for pattern in self.error_patterns:
                if pattern.search(log):
                    error_counts[pattern.pattern] += 1

        return {
            "status": "Success",
            "total_errors_found": len(self.found_errors),
            "summary": dict(error_counts),
            "raw_logs": self.found_errors[-10:] # 最新的 10 筆
        }
