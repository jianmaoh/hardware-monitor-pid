import subprocess
import time
import os
import csv
import multiprocessing
from datetime import datetime

# 設定路徑
PROJECT_ROOT = "/app"
CPP_EXECUTABLE = os.path.join(PROJECT_ROOT, "src", "monitor")
CSV_OUTPUT = os.path.join(PROJECT_ROOT, "data", "pid_thermal_metrics.csv")

def run_cpp_monitor():
    """呼叫 C++ 執行檔並解析輸出"""
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
        print(f"讀取失敗: {e}")
        return None

def log_to_csv(metrics, target_temp, load_factor):
    """將 PID 相關數據寫入 CSV"""
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
    """受控的 CPU 負載核心。根據 shared_load_factor (0.0~1.0) 決定運作與休眠比例"""
    cycle_time = 0.1 # 每個工作週期的總時間 (秒)
    while True:
        load = shared_load_factor.value
        if load <= 0.01:
            time.sleep(cycle_time)
            continue
        
        work_time = cycle_time * load
        sleep_time = cycle_time - work_time
        
        # 執行無意義運算消耗 CPU
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
            
        # 誤差定義：如果目標溫度是 55，當前是 50，誤差為 5 (太冷，需要增加負載)
        # 如果當前是 60，誤差為 -5 (太熱，需要減少負載)
        error = self.target - current_value
        
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt
        
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        
        self.previous_error = error
        self.last_time = current_time
        
        return output

def run_thermal_throttling_test(duration_seconds, target_temp):
    cores = multiprocessing.cpu_count()
    print(f"\n[系統] 偵測到 {cores} 個 CPU 核心。")
    print(f"[系統] 開始 PID 動態熱節流測試，目標溫度維持在: {target_temp}°C")
    
    # 建立多進程共享變數，初始負載設為 1.0 (100%)
    shared_load_factor = multiprocessing.Value('d', 1.0)
    
    processes = []
    for _ in range(cores):
        p = multiprocessing.Process(target=cpu_stress_worker, args=(shared_load_factor,))
        p.start()
        processes.append(p)
    
    # 初始化 PID 控制器 (這些參數 Kp, Ki, Kd 通常需要不斷微調)
    pid = PIDController(kp=0.1, ki=0.02, kd=0.05, target=target_temp)
    
    end_time = time.time() + duration_seconds
    try:
        while time.time() < end_time:
            metrics = run_cpp_monitor()
            if metrics:
                current_temp = metrics['cpu_temp']
                
                # 計算 PID 輸出，並限制負載率在 0.0 到 1.0 之間
                pid_output = pid.compute(current_temp)
                
                # 假設預設負載為 0.5，PID 輸出用來微調這個基準
                new_load = 0.5 + pid_output
                new_load = max(0.0, min(1.0, new_load)) # 限制在 0~100%
                
                shared_load_factor.value = new_load
                
                log_to_csv(metrics, target_temp, new_load)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 實際: {current_temp}°C | 目標: {target_temp}°C | CPU 負載分配: {new_load*100:.1f}%")
                
            time.sleep(1) # 每秒控制一次
            
    finally:
        # 確保無論如何都會關閉子進程
        for p in processes:
            p.terminate()
            p.join()
        print("\n[系統] 測試結束，釋放 CPU 資源。")

def main():
    print("=== 韌體 PID 動態熱節流 (Thermal Throttling) 模擬 ===")
    
    # 刪除舊的測試資料以保持乾淨
    if os.path.exists(CSV_OUTPUT):
        os.remove(CSV_OUTPUT)
        
    # 設定目標溫度為 55°C，執行 40 秒以便觀察 PID 收斂過程
    run_thermal_throttling_test(duration_seconds=40, target_temp=55.0)

if __name__ == "__main__":
    main()
