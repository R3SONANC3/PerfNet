import pandas as pd
import numpy as np

# สร้างข้อมูลเบื้องต้น
timestamps = pd.date_range(start="2024-09-10 13:00:00", periods=10000, freq='30S')
processor_time = np.linspace(10.5, 30.0, 10000)  # เพิ่มขึ้นตามช่วงเวลา
memory_available = np.linspace(2048, 1024, 10000)  # ลดลงตามช่วงเวลา
disk_reads = np.random.normal(32.0, 5, 10000)  # ค่าประมาณ 32.0 โดยมีความแปรผันเล็กน้อย
disk_writes = np.random.normal(25.0, 5, 10000)  # ค่าประมาณ 25.0 โดยมีความแปรผันเล็กน้อย
network_bytes = np.linspace(500000, 1000000, 10000)  # เพิ่มขึ้นตามช่วงเวลา
requests = np.linspace(1000, 5000, 10000)  # เพิ่มขึ้นตามช่วงเวลา

# รวมข้อมูลทั้งหมดเป็น DataFrame
data = pd.DataFrame({
    'Timestamp': timestamps,
    'Processor(_Total) % Processor Time': processor_time,
    'Memory Available MBytes': memory_available,
    'PhysicalDisk(_Total) Disk Reads/sec': disk_reads,
    'PhysicalDisk(_Total) Disk Writes/sec': disk_writes,
    'Network Interface(eth0) Bytes Total/sec': network_bytes,
    'requet': requests
})

# บันทึกข้อมูลเป็นไฟล์ CSV
data.to_csv('data/processed/resource_usage_10000.csv', index=False)

print(data.head())