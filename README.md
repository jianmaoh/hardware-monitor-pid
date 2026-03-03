# 跨平台硬體狀態監控與 PID 動態熱節流模擬
(Cross-Platform Hardware Monitor & PID Thermal Throttling)

## 專案簡介
這是一個模擬嵌入式控制器 (EC) 進行**動態熱能管理**的開源專案。透過 C++ 底層讀取硬體狀態，並結合 Python 自動化控制與 PID 演算法，實現在虛擬化/容器化環境下的閉環控制系統 (Closed-loop control system)。

此專案旨在展示跨語言（C++ & Python）整合能力，以及應對複雜系統測試情境的自動化腳本開發經驗。

## 系統架構
1. **底層資料擷取 (C++)：** 負責即時讀取系統記憶體資訊，並透過 File I/O 接收外部傳遞的真實/模擬硬體溫度。
2. **自動化與控制 (Python)：** - 透過 `subprocess` 跨行程呼叫 C++ 程式獲取數據。
   - 使用 `multiprocessing` 模組模擬 CPU 多核心高負載運作。
   - 實作 **PID 控制器 (Proportional-Integral-Derivative)**，根據目標溫度動態調整 CPU 負載比例 (Load Factor)，防止過熱。
3. **數據視覺化與紀錄：** 將測試過程分為「閒置」、「全載」與「自動節流」階段，即時加上時間戳記寫入 CSV 報表。
4. **環境封裝：** 使用 Docker 封裝開發與測試環境，確保跨平台 (macOS/Linux) 執行的一致性。

## 專案目錄結構
```text
hw_monitor/
├── src/
│   └── monitor.cpp      # C++ 底層數據擷取程式
├── scripts/
│   └── runner.py        # Python 壓力測試與 PID 控制腳本
├── data/
│   └── *.csv            # 結構化監控數據輸出目錄
├── Dockerfile           # Ubuntu 開發環境配置檔
├── mac_agent.sh         # (Optional) macOS 真實 SMC 溫度轉發腳本
└── README.md






