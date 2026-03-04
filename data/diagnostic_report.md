# 系統硬體與日誌綜合診斷報告

**測試時間:** 2026-03-04 14:45:10
**硬體監控數據存放於:** `/app/data/pid_thermal_metrics.csv`

## 系統日誌異常分析 (System Log Anomalies)
- **測試期間發現異常日誌總數:** 4 筆
- **異常類型統計:**
  - `error`: 1 次
  - `hardware`: 1 次
  - `kernel`: 3 次
  - `fail`: 1 次
  - `thermal`: 2 次

### 最新異常日誌樣本 (Top 10 Recent Logs)
```text
Mar  4 10:00:01 ubuntu kernel: [Hardware Error]: Machine check events logged
Mar  4 10:05:12 ubuntu systemd: Failed to start Thermal Daemon Service.
Mar  4 10:10:30 ubuntu kernel: thermal thermal_zone0: critical temperature reached (98 C), shutting down
Mar  4 10:15:00 ubuntu kernel: Normal operation resumed.
```
