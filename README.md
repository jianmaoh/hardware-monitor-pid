## 系統架構
1. **底層資料擷取 (C++)**：負責即時讀取系統記憶體資訊，並透過 File I/O 接收外部傳遞的真實/模擬硬體溫度。
2. **自動化與控制 (Python)**：
   - 實作 **PID 控制器**，根據目標溫度動態調整 CPU 負載比例 (Load Factor)，防止過熱。
3. **AI 驅動根本原因分析 (Agentic Workflow)**：
   - 測試結束後自動掃描 Linux `/var/log/syslog` 捕捉異常。
   - 串接 **Gemini API**，將異常日誌交由 LLM 進行自動化 Root Cause Analysis (RCA)，並產出具備硬體工程師視角的修復建議。
4. **環境封裝與資安實踐**：使用 Docker 封裝跨平台執行環境，並透過 `.gitignore` 確保 API Key 等敏感資訊不外流。

## 專案目錄結構
```text
hw_monitor/
├── src/
│   └── monitor.cpp      # C++ 底層數據擷取程式
├── scripts/
│   ├── runner.py        # Python 壓力測試與 PID 控制腳本
│   ├── log_parser.py    # Linux 系統日誌 Regex 解析模組
│   └── ai_agent.py      # LLM 根本原因分析 API 串接模組
├── data/
│   ├── pid_thermal_metrics.csv  # 結構化監控數據
│   └── diagnostic_report.md     # 包含 AI 分析的綜合診斷報告
├── gemini_api_key.txt   # (Git 忽略) 本機 API 金鑰
├── Dockerfile           # Ubuntu 開發環境配置檔
├── mac_agent.sh         # macOS 真實 SMC 溫度轉發腳本 (Host Sensor)
└── README.md




## Quick Start

### 1. Fetch the code

```bash
git clone [https://github.com/jianmaoh/hardware-monitor-pid.git](https://github.com/jianmaoh/hardware-monitor-pid.git)
cd hardware-monitor-pid
```

### 2. Build the Docker environment

```bash
docker build -t hp_monitor_env .
```

### 3. Launch the container

```bash
docker run -it -v $(pwd):/app hp_monitor_env /bin/bash
```

### 4. Compile and run the test

```bash
g++ src/monitor.cpp -o src/monitor
python3 scripts/runner.py
```






