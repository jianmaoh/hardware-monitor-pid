# 跨平台硬體狀態監控與 PID 動態熱節流模擬
(Cross-Platform Hardware Monitor & PID Thermal Throttling)

## 專案簡介
這是一個模擬嵌入式控制器 (EC) 進行**動態熱能管理**的開源專案。透過 C++ 底層讀取硬體狀態，結合 Python 自動化控制與 PID 演算法，實現在虛擬化/容器化環境下的閉環控制系統 (Closed-loop control system)。
最新版本導入了**系統日誌異常分析 (Log Parsing)**，能夠在硬體壓力測試後，自動化掃描 Linux 系統底層錯誤並產出綜合診斷報告。

## 系統架構
1. **底層資料擷取 (C++)**：負責即時讀取系統記憶體資訊，並透過 File I/O 接收外部傳遞的真實/模擬硬體溫度。
2. **自動化與控制 (Python)**：
   - 透過 `subprocess` 跨行程呼叫 C++ 程式獲取數據。
   - 使用 `multiprocessing` 模組模擬 CPU 多核心高負載運作。
   - 實作 **PID 控制器**，根據目標溫度動態調整 CPU 負載比例 (Load Factor)，防止過熱。
3. **日誌分析與診斷 (Python Regex)**：測試結束後自動掃描 `/var/log/syslog`，利用正規表達式捕捉 `Hardware Error`、`thermal` 等系統級警告。
4. **數據視覺化與紀錄**：即時將 PID 狀態寫入 CSV，並產生包含系統異常統計的 Markdown 綜合診斷報告。
5. **環境封裝**：使用 Docker 封裝開發與測試環境。

## 專案目錄結構
```text
hw_monitor/
├── src/
│   └── monitor.cpp      # C++ 底層數據擷取程式
├── scripts/
│   ├── runner.py        # Python 壓力測試與 PID 控制腳本
│   └── log_parser.py    # Linux 系統日誌 Regex 解析模組
├── data/
│   ├── pid_thermal_metrics.csv  # 結構化監控數據
│   └── diagnostic_report.md     # 綜合診斷報告 (自動生成)
├── Dockerfile           # Ubuntu 開發環境配置檔
├── mac_agent.sh         # macOS 真實 SMC 溫度轉發腳本
└── README.md





