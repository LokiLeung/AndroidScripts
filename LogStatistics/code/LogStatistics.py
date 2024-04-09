import subprocess
import os
import time
import threading

# Global variables
process_names = {}  # Dictionary to store process names


# Step 0: Clear log buffer and set buffer size limit
def prepare_logcat():
    try:
        subprocess.run(['adb', 'shell', 'logcat', '-c'])
        subprocess.run(['adb', 'shell', 'logcat', '-G', '256M'])
    except Exception as e:
        print("Error:", e)


# Function to get process names periodically
def update_process_names(interval):
    global process_names
    while True:
        try:
            output = subprocess.check_output(['adb', 'shell', 'ps', '-A']).decode('utf-8')
            lines = output.split('\n')
            for line in lines[1:]:  # Skip the header
                parts = line.split()
                if len(parts) >= 9:
                    pid = parts[1]
                    name = parts[-1]
                    process_names[pid] = name
        except Exception as e:
            print("Error updating process names:", e)
        time.sleep(interval)


# Step 1: Capture logs using 'adb shell logcat -v threadtime' command
def capture_logs(duration):
    log_file = "logs.txt"
    try:
        with open(log_file, "w", errors="replace") as f:  # 使用更宽松的错误处理模式
            process = subprocess.Popen(['adb', 'shell', 'logcat', '-v', 'threadtime', '*:D'], stdout=subprocess.PIPE)
            time_end = time.time() + duration
            line_number = 1
            while time.time() < time_end:
                line = process.stdout.readline().decode('utf-8', errors='replace').strip()  # 使用更宽松的错误处理模式
                if line:
                    f.write(line + '\n')
                    print(line)  # 实时显示日志，如果不需要可以删除这行
                    line_number += 1
    except Exception as e:
        print("Error:", e)


# Step 3: Parse and save logs
def parse_and_save_logs():
    global process_names
    parsed_logs = {}
    try:
        with open("logs.txt", "r", errors="replace") as f:
            for line_number, line in enumerate(f, start=1):
                parts = line.strip().split()
                if len(parts) >= 6:
                    timestamp = parts[0] + ' ' + parts[1]
                    process_id = parts[2]
                    thread_id = parts[3]
                    log_level = parts[4]
                    tag = parts[5]
                    log_message = ' '.join(parts[6:])
                    byte_size = len(line.encode('utf-8'))  # Get the size of the line in bytes
                    process_name = process_names.get(process_id, 'Unknown')

                    parsed_logs[line_number] = {
                        'process_name': process_name,
                        'timestamp': timestamp,
                        'process_id': process_id,
                        'thread_id': thread_id,
                        'log_level': log_level,
                        'tag': tag,
                        'log_message': log_message,
                        'byte_size': byte_size
                    }
    except FileNotFoundError:
        print("Log file not found. Please capture logs first.")
    except Exception as e:
        print("Error:", e)
    return parsed_logs


def print_logs_by_process(parsed_logs):
    process_logs = {}
    for line_number, log in parsed_logs.items():
        process_id = log['process_id']
        if process_id not in process_logs:
            process_logs[process_id] = []
        process_logs[process_id].append(log)

    total_lines = sum(len(logs) for logs in process_logs.values())
    total_bytes = sum(log['byte_size'] for logs in parsed_logs.values())

    print("进程名".ljust(50) + "| 进程号 ".ljust(10) + "| 日志等级分配".ljust(50) + "| 总共多少行".ljust(
        10) + "| 总共多少字节".ljust(20) + "| 行数百分比".ljust(20) + "| 字节百分比".ljust(20))

    # Sort process logs by process id
    sorted_process_logs = sorted(process_logs.items(), key=lambda x: x[0])

    for process_id, logs in sorted_process_logs:
        log_levels = {'I': 0, 'D': 0, 'W': 0, 'E': 0, 'V': 0}
        for log in logs:
            # Check if log level exists in the dictionary before incrementing
            log_levels[log['log_level']] = log_levels.get(log['log_level'], 0) + 1
        log_level_distribution = ', '.join([f"{level}:{count}" for level, count in log_levels.items()]).ljust(50)
        process_name = logs[0]['process_name'].ljust(50)  # No need to encode process name
        process_name = process_name.encode('utf-8', errors='ignore').decode('utf-8')  # Handle non-ASCII characters
        line_percent = "{:.2f}%".format(len(logs) / total_lines * 100) if total_lines != 0 else "0.00%"
        byte_percent = "{:.2f}%".format(
            sum(log['byte_size'] for log in logs) / total_bytes * 100) if total_bytes != 0 else "0.00%"
        print(
            f"{process_name} | {process_id.ljust(10)} | {log_level_distribution} | {str(len(logs)).ljust(10)} | {str(sum(log['byte_size'] for log in logs)).ljust(20)} | {line_percent.ljust(20)} | {byte_percent.ljust(20)}")

    print(
        f"{'Total'.ljust(50)} | {str(len(process_logs)).ljust(10)} | {str(total_lines).ljust(10)} | {str(total_bytes).ljust(20)}")


# Function to get process names
def get_process_names():
    process_names = {}
    try:
        output = subprocess.check_output(['adb', 'shell', 'ps', '-A']).decode('utf-8')
        lines = output.split('\n')
        for line in lines[1:]:  # Skip the header
            parts = line.split()
            if len(parts) >= 9:
                pid = parts[1]
                name = parts[-1]
                process_names[pid] = name
    except Exception as e:
        print("Error:", e)
    return process_names


if __name__ == "__main__":
    # Step 0
    prepare_logcat()

    # Step 1
    duration = 60  # Capture logs for 30 minutes
    capture_thread = threading.Thread(target=capture_logs, args=(duration,))
    capture_thread.start()

    # Start thread to update process names every 10 seconds
    update_process_thread = threading.Thread(target=update_process_names, args=(10,))
    update_process_thread.daemon = True  # Set as daemon thread to terminate when main program exits
    update_process_thread.start()

    # Wait for the capture thread to finish
    capture_thread.join()

    # Step 3
    parsed_logs = parse_and_save_logs()

    # Step 4
    print_logs_by_process(parsed_logs)
