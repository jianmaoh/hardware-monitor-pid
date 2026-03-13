import google.generativeai as genai
import os

class FirmwareAIAgent:
    def __init__(self):
        # Set the path for the API key file
        key_file_path = "/app/gemini_api_key.txt"
        self.api_key = None
        
        # 1. Try reading the key file first (Local development environment)
        if os.path.exists(key_file_path):
            with open(key_file_path, 'r', encoding='utf-8') as f:
                self.api_key = f.read().strip()
        # 2. If the file does not exist, try reading the environment variable (CI/CD environment)
        else:
            self.api_key = os.environ.get("GEMINI_API_KEY")
                
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    def analyze_error_logs(self, logs_list):
        """Send error logs to AI for analysis and return root cause and recommendations"""
        if not self.model:
            return "⚠️ /app/gemini_api_key.txt not found and environment variable not set. Skipping AI root cause analysis."
            
        if not logs_list:
            return "No abnormal logs to analyze."

        log_text = "\n".join(logs_list)
        
        prompt = f"""
        You are a Senior System Firmware Engineer at HP.
        Below are the abnormal Linux system logs captured during stress testing:
        
        ```text
        {log_text}
        ```
        
        Please provide a concise analysis report containing the following two sections:
        1. **Root Cause Analysis**: Determine the underlying hardware or OS causes of these errors.
        2. **Action Items**: Provide a bulleted list of troubleshooting or repair steps.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI analysis exception occurred: {e}"
