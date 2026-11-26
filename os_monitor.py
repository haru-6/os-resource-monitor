import time
import os
import csv
from datetime import datetime
import psutil
import pandas as pd
import matplotlib.pyplot as plt

# Configuration Parameters
LOG_FILE = "system_metrics_log.csv"
POLL_INTERVAL = 2  # seconds
DURATION = 60      # total run time for testing (seconds)

# Thresholds
CPU_THRESHOLD = 80.0    # percent
MEMORY_THRESHOLD = 85.0 # percent
DISK_THRESHOLD = 90.0   # percent

def initialize_log():
    """Initializes the CSV log file with headers if it doesn't exist."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "CPU_Percent", "Memory_Percent", "Disk_Percent", "Alerts"])

def log_metrics(cpu, memory, disk, alerts):
    """Appends a timestamped record of metrics and alerts to the CSV."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_str = "; ".join(alerts) if alerts else "None"
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, cpu, memory, disk, alert_str])

def check_thresholds(cpu, memory, disk):
    """Evaluates metrics against configured thresholds and returns alerts."""
    alerts = []
    if cpu > CPU_THRESHOLD:
        alerts.append(f"HIGH_CPU: {cpu}%")
    if memory > MEMORY_THRESHOLD:
        alerts.append(f"HIGH_MEMORY: {memory}%")
    if disk > DISK_THRESHOLD:
        alerts.append(f"HIGH_DISK: {disk}%")
    return alerts

def monitor_loop():
    """Main loop to poll OS metrics, evaluate alerts, and log data."""
    initialize_log()
    print(f"[*] Starting OS Resource Monitor... Logging to {LOG_FILE}")
    print(f"[*] Polling every {POLL_INTERVAL}s for {DURATION}s.\n")
    
    start_time = time.time()
    try:
        while time.time() - start_time < DURATION:
            # Fetch system metrics
            cpu_val = psutil.cpu_percent(interval=None)
            memory_val = psutil.virtual_memory().percent
            disk_val = psutil.disk_usage('/').percent
            
            # Evaluate thresholds
            alerts = check_thresholds(cpu_val, memory_val, disk_val)
            
            # Log data
            log_metrics(cpu_val, memory_val, disk_val, alerts)
            
            # Console output
            print(f"[{datetime.now().strftime('%H:%M:%S' )}] CPU: {cpu_val}% | MEM: {memory_val}% | DISK: {disk_val}%", end="")
            if alerts:
                print(f" --> ALERTS: {alerts}")
            else:
                print(" --> Status: OK")
                
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n[!] Monitoring stopped by user.")

def generate_graphs():
    """Reads the CSV log and generates visualization graphs."""
    if not os.path.exists(LOG_FILE):
        print("[!] No log file found for graphing.")
        return
        
    print("\n[*] Generating resource utilization graphs...")
    df = pd.read_csv(LOG_FILE)
    
    # Convert Timestamp string to datetime objects for clean plotting
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    plt.figure(figsize=(10, 5))
    plt.plot(df['Timestamp'], df['CPU_Percent'], label='CPU Usage (%)', color='red', marker='o', markersize=3)
    plt.plot(df['Timestamp'], df['Memory_Percent'], label='Memory Usage (%)', color='blue', marker='s', markersize=3)
    plt.plot(df['Timestamp'], df['Disk_Percent'], label='Disk Usage (%)', color='green', linestyle='--')
    
    plt.axhline(y=CPU_THRESHOLD, color='orange', linestyle=':', label='CPU Threshold')
    
    plt.xlabel('Time')
    plt.ylabel('Percentage (%)')
    plt.title('OS Resource Monitoring & Utilization Trends')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    output_image = "resource_trends.png"
    plt.savefig(output_image)
    print(f"[+] Graph successfully saved as '{output_image}'.")
    plt.show()

if __name__ == "__main__":
    monitor_loop()
    generate_graphs()