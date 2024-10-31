import openai
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import time
from datetime import datetime, timedelta

# ตั้งค่า API Key สำหรับ OpenAI
# ฟังก์ชันสำหรับการตรวจสอบประสิทธิภาพผ่าน OpenAI
def check_performance_with_openai(time_stamp, response_time, response_code, success, failure_message, url, latency, connect):
    prompt = f"""
    You are a performance testing expert. We have collected some performance test data and would like your analysis.
    
    Here are the specific details:
    - TimeStamp: {time_stamp}
    - Response Time (Elapsed): {response_time} ms
    - Response Code: {response_code}
    - Success: {success}
    - Failure Message: {failure_message}
    - URL: {url}
    - Latency: {latency} ms
    - Connect: {connect} ms
    
    Based on this data, is the response time:
    - Good 
    - About to be problematic
    - Not good

    if it Good Respond just Good
    
    Respond with only one of the above options.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in performance testing."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response['choices'][0]['message']['content'].strip()

# โหลดข้อมูลจากไฟล์ CSV
log_data = pd.read_csv('data/JmeterLoadTest_10users_20240914125521.csv')

# ฟังก์ชันเพื่อปรับเปลี่ยน Timestamp ให้กับแต่ละแถว
def adjust_timestamps(log_data):
    start_time = datetime.fromtimestamp(log_data['timeStamp'].iloc[0] / 1000)
    adjusted_timestamps = []
    for i in range(len(log_data)):
        new_time = start_time + timedelta(seconds=5 * i)
        adjusted_timestamps.append(new_time.timestamp() * 1000) # แปลงกลับไปเป็น milliseconds
    log_data['adjusted_timeStamp'] = adjusted_timestamps

adjust_timestamps(log_data)

# ข้อมูลที่จะเก็บสำหรับการอัพเดตกราฟ
timestamps = []
response_times = []

# สร้างกราฟ
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-o', markersize=4)  # ออบเจกต์เส้นกราฟ
ax.set_xlabel('Timestamp Index')
ax.set_ylabel('Response Time (Elapsed)')
ax.set_title('Real-Time Response Time Over Time')

# ฟังก์ชันในการอัพเดตกราฟ
def update_graph(frame):
    line.set_data(range(len(timestamps)), response_times)
    ax.relim()  # วิเคราะห์ข้อมูลที่วางบนกราฟใหม่
    ax.autoscale_view()  # ปรับขนาดกราฟอัตโนมัติ
    return line,

# สร้างแอนิเมชั่น
ani = animation.FuncAnimation(fig, update_graph, blit=True, interval=100)  # ลด interval เพื่อทำให้กราฟอัพเดทเร็วขึ้น

def collect_data():
    for index, row in log_data.iterrows():
        try:
            time_stamp = row['adjusted_timeStamp']
            response_time = row['elapsed']
            response_code = row['responseCode']
            success = row['success']
            failure_message = row.get('failureMessage', 'N/A')  # กำหนดค่าเริ่มต้นถ้า column นี้ไม่มี
            url = row['URL']
            latency = row['Latency']
            connect = row['Connect']
            
            analysis_result = check_performance_with_openai(time_stamp, response_time, response_code, success, failure_message, url, latency, connect)
            
            if analysis_result == "Good":
                print("Good")
            else:
                print(f"Timestamp: {time_stamp}, Elapsed: {response_time}, Analysis: {analysis_result}")
                print(f"Additional Info - URL: {url}, Response Code: {response_code}, Success: {success}, Failure Message: {failure_message}, Latency: {latency}, Connect: {connect}")
                
            timestamps.append(time_stamp)
            response_times.append(response_time)
        except Exception as e:
            print(f"Error at Timestamp {time_stamp}: {str(e)}")
        time.sleep(0.1)  # ลด delay เพื่อเพิ่มความเร็วในการทำงาน

# ใช้ threading เพื่อให้กระบวนการตรวจสอบข้อมูลทำงานแบบคู่ขนานกับกระบวนการอัพเดตกราฟ
thread = threading.Thread(target=collect_data)
thread.start()

# แสดงกราฟ
plt.show()

# รอให้การเก็บข้อมูลเสร็จสมบูรณ์ก่อนปิด
thread.join()

