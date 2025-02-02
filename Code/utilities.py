from datetime import datetime
import psutil
import os
import time
from collections import defaultdict


def getSystemStats():
    """
    Returns a dictionary with system stats like CPU usage, RAM usage.
    """
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_used = ram.percent
    ram_free = ram.available * 100 / ram.total

    return {
        "cpu": cpu,
        "ram_used": ram_used,
        "ram_free": ram_free,
        "total_ram": ram.total
    }


def getDiskInfo():
    """
    Returns a dictionary with disk usage info (percent, used, free).
    """
    disk = psutil.disk_usage('/')
    return {
        "percent": disk.percent,
        "used": disk.used,
        "free": disk.free
    }


_prev_disk_info = None  # Store previous disk info
_prev_timestamp = None  # Store the timestamp of the previous call


def getDiskRunInfo():
    """
    Returns a dictionary with disk read/write speeds in KB/s.
    """
    global _prev_disk_info, _prev_timestamp

    # Get current disk I/O stats and timestamp
    current_disk_info = psutil.disk_io_counters()
    current_timestamp = time.time()

    if _prev_disk_info is None or _prev_timestamp is None:
        # Initialize previous data on the first call
        _prev_disk_info = current_disk_info
        _prev_timestamp = current_timestamp
        return {
            "read_kbps": 0,
            "write_kbps": 0
        }

    # Calculate elapsed time in seconds
    elapsed_time = current_timestamp - _prev_timestamp

    # Calculate read/write speeds in KB/s
    read_kbps = (current_disk_info.read_bytes -
                 _prev_disk_info.read_bytes) / elapsed_time / 1024
    write_kbps = (current_disk_info.write_bytes -
                  _prev_disk_info.write_bytes) / elapsed_time / 1024

    # Update previous values
    _prev_disk_info = current_disk_info
    _prev_timestamp = current_timestamp

    return {
        "read_kbps": read_kbps,
        "write_kbps": write_kbps
    }


def getProcesses():
    """
    Returns a list of main processes (grouped by name) with aggregated CPU%, memory (MB/KB),
    and the PID of the first process in each group, along with additional info like memory unit.
    """
    cpu_count = psutil.cpu_count(
        logical=True)  # Get the number of logical CPU cores
    process_data = defaultdict(lambda: {"cpu_percent": 0.0, "memory": 0.0, "memory_unit": "MB", "pid": None,
                                        "user": "Unknown", "status": "N/A", "disk_io_read_write": "N/A",
                                        "network_io_receive_send": "N/A", "priority": "Normal",
                                        "threads": 0, "uptime": "N/A", "executable_path": "N/A",
                                        "parent_pid": None, "process_type": "N/A"})

    for proc in psutil.process_iter(['name', 'pid', 'cpu_percent', 'username', 'status', 'num_threads', 'exe', 'create_time']):
        try:
            proc_name = proc.info['name'] or "Unknown"
            if process_data[proc_name]["pid"] is None:
                # Store the first PID
                process_data[proc_name]["pid"] = proc.info['pid']

            process_data[proc_name]["cpu_percent"] += proc.info['cpu_percent'] / \
                (cpu_count or 1)

            memory_info = proc.memory_info()
            memory_bytes = memory_info.rss
            if memory_bytes >= 1024 * 1024:  # If memory is greater than or equal to 1 MB
                memory_mb = memory_bytes / 1024 / 1024  # Convert to MB
                process_data[proc_name]["memory"] += memory_mb
                process_data[proc_name]["memory_unit"] = "MB"  # Set unit as MB
            else:
                memory_kb = memory_bytes / 1024  # Convert to KB if less than 1 MB
                process_data[proc_name]["memory"] += memory_kb
                process_data[proc_name]["memory_unit"] = "KB"  # Set unit as KB

            process_data[proc_name]["user"] = proc.info['username'] or "Unknown"
            process_data[proc_name]["status"] = proc.info['status'] or "N/A"
            process_data[proc_name]["threads"] = proc.info['num_threads'] or 0
            process_data[proc_name]["executable_path"] = proc.info['exe'] or "N/A"

            # Handle parent process separately
            parent_proc = proc.parent()  # Access the parent process
            process_data[proc_name]["parent_pid"] = parent_proc.pid if parent_proc else "N/A"

            # Disk I/O (Placeholder, requires more advanced methods to gather per-process I/O)
            process_data[proc_name]["disk_io_read_write"] = "N/A"

            # Network I/O (Placeholder, requires more advanced methods to gather per-process I/O)
            process_data[proc_name]["network_io_receive_send"] = "N/A"

            # Process priority
            # Get the process priority using nice value
            process_data[proc_name]["priority"] = proc.nice()

            # Process uptime (current time - process start time)
            uptime_seconds = int(
                datetime.now().timestamp() - proc.info['create_time'])
            process_data[proc_name]["uptime"] = f"{uptime_seconds} seconds"

            # Process type (e.g., whether it’s a system or user process)
            process_data[proc_name]["process_type"] = "N/A"  # Placeholder

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
            continue

    # Convert the aggregated data to a list of dictionaries
    processes = []
    for name, stats in process_data.items():
        processes.append({
            "pid": stats["pid"],
            "name": name,
            "cpu_percent": round(stats["cpu_percent"], 1),
            "memory": round(stats["memory"]),  # Memory in MB/KB
            "memory_unit": stats["memory_unit"],  # Memory unit (MB/KB)
            "user": stats["user"],
            "status": stats["status"],
            "disk_io_read_write": stats["disk_io_read_write"],
            "network_io_receive_send": stats["network_io_receive_send"],
            "priority": stats["priority"],
            "threads": stats["threads"],
            "uptime": stats["uptime"],
            "executable_path": stats["executable_path"],
            "parent_pid": stats["parent_pid"],
            "process_type": stats["process_type"]
        })

    # Sort by CPU usage descending, then memory usage descending
    processes.sort(key=lambda x: (x["cpu_percent"], x["memory"]), reverse=True)

    return processes


def update_system_data(cpu_data, ram_data, disk_data):
    """
    Updates the system stats data (CPU, RAM, Disk) for graphs or any other use.
    Arguments:
    cpu_data -- List to store CPU data
    ram_data -- List to store RAM data
    disk_data -- List to store Disk data
    """
    system_stats = getSystemStats()
    disk_stats = getDiskInfo()
    disk_run_info = getDiskRunInfo()

    # Append the current data to the respective lists
    cpu_data.append(system_stats["cpu"])
    ram_data.append(system_stats["ram_used"]*system_stats["total_ram"])
    # Convert bytes to MB
    disk_data.append(disk_run_info["read_kbps"])

    return cpu_data, ram_data, disk_data


def get_network_stats():
    net_io = psutil.net_io_counters()
    download = net_io.bytes_recv / (1024 * 1024)  # Convert to MB
    upload = net_io.bytes_sent / (1024 * 1024)    # Convert to MB
    return {"download": download, "upload": upload}


# utilities.py


def kill_process(pid):
    """Kill a process by its PID."""
    try:
        process = psutil.Process(pid)
        process.terminate()  # Or use process.kill() for forceful termination
        return True
    except psutil.NoSuchProcess:
        return False
    except psutil.AccessDenied:
        return False


def format_memory(memory_bytes):
    """Format memory in MB or KB."""
    if memory_bytes >= 1024 * 1024:
        # Convert bytes to MB
        return f"{memory_bytes / (1024 * 1024):.2f} MB"
    elif memory_bytes >= 1024:
        # Convert bytes to KB
        return f"{memory_bytes / 1024:.2f} KB"
    else:
        return f"{memory_bytes} bytes"


def show_details(pid):
    """Get details of a process by its PID."""
    try:
        process = psutil.Process(pid)
        details = {
            'name': process.name(),
            'exe': process.exe(),
            'status': process.status(),
            'cpu_percent': process.cpu_percent(interval=1.0),
            # Format memory as MB or KB
            'memory_info': format_memory(process.memory_info().rss),
            'create_time': process.create_time(),
            'cmdline': process.cmdline(),
        }
        return details
    except psutil.NoSuchProcess:
        return None
    except psutil.AccessDenied:
        return None
