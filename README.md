## System Architecture
1. **Low-Level Data Acquisition (C++)**: Responsible for real-time reading of system memory information and receiving real/simulated hardware temperatures passed externally via File I/O.
2. **Automation and Control (Python)**:
   - Implements a **PID Controller** to dynamically adjust the CPU load factor based on the target temperature to prevent overheating.
3. **AI-Driven Root Cause Analysis (Agentic Workflow)**:
   - Automatically scans Linux `/var/log/syslog` to capture anomalies after the test completes.
   - Integrates the **Gemini API** to pass anomaly logs to the LLM for automated Root Cause Analysis (RCA), generating repair recommendations from a hardware engineer's perspective.
4. **Environment Encapsulation & Security Practices**: Uses Docker to encapsulate a cross-platform execution environment and ensures sensitive information like API keys is not leaked via `.gitignore`.

## Project Directory Structure
```text
hw_monitor/
├── src/
│   └── monitor.cpp      # C++ low-level data acquisition program
├── scripts/
│   ├── runner.py        # Python stress test and PID control script
│   ├── log_parser.py    # Linux system log Regex parsing module
│   └── ai_agent.py      # LLM RCA API integration module
├── data/
│   ├── pid_thermal_metrics.csv  # Structured monitoring data
│   └── diagnostic_report.md     # Comprehensive diagnostic report including AI analysis
├── gemini_api_key.txt   # (Git ignored) Local API key
├── Dockerfile           # Ubuntu development environment configuration file
├── mac_agent.sh         # macOS real SMC temperature forwarding script (Host Sensor)
└── README.md

```
## Quick Start (For macOS)

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

### 4. Run mac_agent.sh on another terminal page to get the real-time temperature
```bash
./mac_agent.sh 
```


### 5. Compile and run the test

```bash
g++ src/monitor.cpp -o src/monitor
python3 scripts/runner.py
```






