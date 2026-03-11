import google.generativeai as genai
import os

class FirmwareAIAgent:
    def __init__(self):
        # 設定密鑰檔案的路徑
        key_file_path = "/app/gemini_api_key.txt"
        self.api_key = None
        
        # 1. 先嘗試讀取密鑰檔案 (本地開發環境)
        if os.path.exists(key_file_path):
            with open(key_file_path, 'r', encoding='utf-8') as f:
                self.api_key = f.read().strip()
        # 2. 如果檔案不存在，則嘗試讀取環境變數 (CI/CD 環境)
        else:
            self.api_key = os.environ.get("GEMINI_API_KEY")
                
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    def analyze_error_logs(self, logs_list):
        """將錯誤日誌送交 AI 分析並回傳根本原因與建議"""
        if not self.model:
            return "⚠️ 找不到 /app/gemini_api_key.txt 檔案，也未設定環境變數，跳過 AI 根本原因分析。"
            
        if not logs_list:
            return "無異常日誌需分析。"

        log_text = "\n".join(logs_list)
        
        prompt = f"""
        你是一位任職於 HP 的資深系統韌體工程師 (Firmware Engineer)。
        以下是壓力測試期間捕捉到的 Linux 系統異常日誌：
        
        ```text
        {log_text}
        ```
        
        請提供精簡的分析報告，包含以下兩個段落：
        1. **根本原因分析 (Root Cause Analysis)**：判斷造成這些錯誤的底層硬體或作業系統原因。
        2. **修復建議 (Action Items)**：條列式提供後續的排錯或修復步驟。
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI 分析發生例外錯誤: {e}"

