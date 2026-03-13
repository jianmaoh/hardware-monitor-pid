import subprocess
import time
import os
import csv
import multiprocessing
from datetime import datetime
from log_parser import LinuxLogAnalyzer
from ai_agent import FirmwareAIAgent
import json

# set the path
PROJECT_ROOT = "/app"
CPP_EXECUTABLE = os.path.join(PROJECT_ROOT, "src", "monitor")
CSV_OUTPUT = os.path.join(PROJECT_ROOT, "data", "pid_thermal_metrics.csv")

def run_cpp_monitor():
    """Call the C++ executable and parse the output"""
    try:
        result = subprocess.run([CPP_EXECUTABLE], capture_output=True, text=True, check=True)
        output_lines = result.stdout.strip().split('\n')
        metrics = {}
        for line in output_lines:
            if "CPU_TEMP_C:" in line:
                metrics["cpu_temp"] = float(line.split(":")[1].strip())
            elif "MemTotal:" in line:
                metrics["mem_total"] = line.split(":")[1].replace("kB", "").strip()
            elif "MemFree:" in line:
                metrics["mem_free"] = line.split(":")[1].replace("kB", "").strip()
        return metrics
    except Exception as e:
        print(f"Read failed: {e}")
        return None

def log_to_csv(metrics, target_temp, load_factor):
    """Log PID related metrics to CSV"""
    if not metrics:
        return
    file_exists = os.path.isfile(CSV_OUTPUT)
    with open(CSV_OUTPUT, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Timestamp', 'Current_Temp_C', 'Target_Temp_C', 'Load_Factor', 'MemFree_kB'])
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([
            timestamp, 
            metrics.get("cpu_temp", "N/A"),
            target_temp,
            round(load_factor, 3),
            metrics.get("mem_free", "N/A")
        ])

def cpu_stress_worker(shared_load_factor):
    """Controlled CPU load core. Determines work/sleep ratio based on shared_load_factor (0.0~1.0)"""
    cycle_time = 0.1 # Total time per work cycle (seconds)
    while True:
        load = shared_load_factor.value
        if load <= 0.01:
            time.sleep(cycle_time)
            continue
        
        work_time = cycle_time * load
        sleep_time = cycle_time - work_time
        
        # Execute meaningless calculations to consume CPU
        start = time.time()
        while time.time() - start < work_time:
            _ = 123456789 * 987654321
            
        if sleep_time > 0:
            time.sleep(sleep_time)

class PIDController:
    def __init__(self, kp, ki, kd, target):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.target = target
        self.integral = 0
        self.previous_error = 0
        self.last_time = time.time()

    def compute(self, current_value):
        current_time = time.time()
        dt = current_time - self.last_time
        if dt <= 0.0:
            dt = 1e-16
            
        # Error definition: If target is 55 and current is 50, error is 5 (too cold, need to increase load)
        # If current is 60, error is -5 (too hot, need to decrease load)
        error = self.target - current_value
        
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt
        
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        
        self.previous_error = error
        self.last_time = current_time
        
        return output

def run_thermal_throttling_test(duration_seconds, target_temp):
    cores = multiprocessing.cpu_count()
    print(f"\n[System] Detected {cores} CPU cores.")
    print(f"[System] Starting PID dynamic thermal throttling test, target temperature maintained at: {target_temp}°C")
    
    # Create a multi-processing shared variable, initial load set to 1.0 (100%)
    shared_load_factor = multiprocessing.Value('d', 1.0)
    
    processes = []
    for _ in range(cores):
        p = multiprocessing.Process(target=cpu_stress_worker, args=(shared_load_factor,))
        p.start()
        processes.append(p)
    
    # Initialize PID controller (Kp, Ki, Kd parameters usually need fine-tuning)
    pid = PIDController(kp=0.1, ki=0.02, kd=0.05, target=target_temp)
    
    end_time = time.time() + duration_seconds
    try:
        while time.time() < end_time:
            metrics = run_cpp_monitor()
            if metrics:
                current_temp = metrics['cpu_temp']
                
                # Calculate PID output, and limit load ratio between 0.0 and 1.0
                pid_output = pid.compute(current_temp)
                
                # Assume default load is 0.5, PID output is used to fine-tune this baseline
                new_load = 0.5 + pid_output
                new_load = max(0.0, min(1.0, new_load)) # Limit to 0~100%
                
                shared_load_factor.value = new_load
                
                log_to_csv(metrics, target_temp, new_load)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Current: {current_temp}°C | Target: {target_temp}°C | CPU Load Allocation: {new_load*100:.1f}%")
                
            time.sleep(1) # Control once per second
            
    finally:
        # Ensure child processes are terminated no matter what
        for p in processes:
            p.terminate()
            p.join()
        print("\n[System] Test completed, releasing CPU resources.")

def generate_diagnostic_report(log_summary, csv_path, ai_analysis_result=""):
    """Generate a comprehensive diagnostic report in Markdown format"""
    report_path = os.path.join(PROJECT_ROOT, "data", "diagnostic_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Hardware and System Log Comprehensive Diagnostic Report\n\n")
        f.write(f"**Test Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Hardware Monitor Metrics stored in:** `{csv_path}`\n\n")
        
        f.write("## 1. System Log Anomalies Statistics\n")
        if log_summary['status'] == 'Success':
            f.write(f"- **Total abnormal logs found during test:** {log_summary['total_errors_found']}\n")
            for err_type, count in log_summary['summary'].items():
                f.write(f"  - `{err_type}`: {count} times\n")
            
            f.write("\n### Latest Abnormal Log Samples\n")
            f.write("```text\n")
            for log in log_summary['raw_logs']:
                f.write(f"{log}\n")
            f.write("```\n\n")
        else:
            f.write(f"Log read failed: {log_summary['status']}\n\n")
            
        # Add AI analysis result section
        f.write("## 2. AI-Driven Root Cause Analysis (RCA)\n")
        f.write(ai_analysis_result + "\n")
            
    print(f"\n[System] Comprehensive diagnostic report generated: {report_path}")

def generate_mock_syslog():
    """Generate mock Linux hardware and system error logs in /var/log (10 entries in total)"""
    mock_logs = [
        "Mar  4 10:00:01 ubuntu kernel: [Hardware Error]: Machine check events logged\n",
        "Mar  4 10:02:15 ubuntu kernel: ACPI Error: AE_NOT_FOUND, While resolving a named reference package element (20210730/dspkginit-438)\n",
        "Mar  4 10:05:12 ubuntu systemd: Failed to start Thermal Daemon Service.\n",
        "Mar  4 10:06:22 ubuntu kernel: pcieport 0000:00:1c.0: PCIe Bus Error: severity=Corrected, type=Physical Layer, (Receiver ID)\n",
        "Mar  4 10:08:05 ubuntu kernel: mce: [Hardware Error]: CPU 2: Machine Check: 0 Bank 4: e600000000020408\n",
        "Mar  4 10:09:10 ubuntu kernel: EDAC MC0: 1 CE memory read error on CPU_SrcID#0_Ha#0_Chan#1_DIMM#0 (channel:1 slot:0 page:0x12345 offset:0x0)\n",
        "Mar  4 10:09:45 ubuntu kernel: CPU4: Package temperature above threshold, cpu clock throttled (total events = 1)\n",
        "Mar  4 10:10:30 ubuntu kernel: thermal thermal_zone0: critical temperature reached (98 C), shutting down\n",
        "Mar  4 10:12:05 ubuntu kernel: ACPI Warning: \\_SB.BAT0: Battery state not reporting correctly.\n",
        "Mar  4 10:15:00 ubuntu kernel: Normal operation resumed.\n"
    ]
    
    # Write directly to Linux default log path
    with open("/var/log/syslog", "w", encoding="utf-8") as f:
        f.writelines(mock_logs)
    print("[System] Mock /var/log/syslog (including ACPI, MCE, PCIe errors) generated for parser testing.")

def main():
    print("=== Firmware PID Dynamic Thermal Throttling & Log Analysis Simulation ===")
    
    # Record test start time
    test_start_time = datetime.now()
    
    if os.path.exists(CSV_OUTPUT):
        os.remove(CSV_OUTPUT)
        
    run_thermal_throttling_test(duration_seconds=30, target_temp=55.0)
    
    # After testing, start log analysis
    print("\n[System] Starting to parse Linux system log (/var/log/syslog)...")
    generate_mock_syslog() 
    
    analyzer = LinuxLogAnalyzer()
    log_summary = analyzer.analyze_recent_logs()
    
    # Start AI analysis
    ai_result = "No abnormal logs, analysis not required."
    if log_summary.get('total_errors_found', 0) > 0:
        print("[System] Anomalies detected, calling AI for root cause analysis...")
        ai_agent = FirmwareAIAgent()
        ai_result = ai_agent.analyze_error_logs(log_summary['raw_logs'])
    
    generate_diagnostic_report(log_summary, CSV_OUTPUT, ai_result)

if __name__ == "__main__":
    main()
