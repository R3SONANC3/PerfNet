import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# 1. เตรียมข้อมูล (Input data)
data = {
    'Timestamp': [
        '09/10/2024 13:00:00', '09/10/2024 13:00:30', '09/10/2024 13:01:00',
        '09/10/2024 13:01:30', '09/10/2024 13:02:00', '09/10/2024 13:02:30'
    ],
    'Processor_Time': [10.5, 12.3, 14.8, 16.7, 18.4, 20.1],
    'Memory_Available': [2048, 1980, 1950, 1920, 1880, 1850],
    'Disk_Reads': [30.0, 35.0, 32.0, 33.0, 34.0, 31.0],
    'Disk_Writes': [20.0, 22.0, 25.0, 27.0, 29.0, 24.0],
    'Network_Bytes': [500000, 510000, 520000, 530000, 540000, 550000]
}

# Convert to DataFrame
df = pd.DataFrame(data)
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# 2. สร้างฟีเจอร์ใหม่จาก Timestamp เช่นการแปลงเป็นเลข Unix หรือดึงชั่วโมง นาที ออกมา
df['Time_delta'] = (df['Timestamp'] - df['Timestamp'].min()).dt.total_seconds()

# ฟีเจอร์ที่ใช้ในการฝึกโมเดล
X = df[['Time_delta', 'Memory_Available', 'Disk_Reads', 'Disk_Writes', 'Network_Bytes']]
y = df['Processor_Time']

# 3. แบ่งข้อมูลสำหรับการฝึกโมเดลและทดสอบโมเดล
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. สร้างโมเดล Linear Regression
model = LinearRegression()

# ฝึกโมเดล
model.fit(X_train, y_train)

# 5. ทำนายการใช้ CPU บนชุดข้อมูลทดสอบ
y_pred = model.predict(X_test)

# 6. ประเมินโมเดลด้วยค่า Mean Squared Error (MSE)
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')

# 7. แสดงการทำนายและค่าจริง
plt.figure(figsize=(10, 5))
plt.plot(y_test.values, label='True Processor Time')
plt.plot(y_pred, label='Predicted Processor Time')
plt.legend()
plt.title('True vs Predicted % Processor Time')
plt.show()

# 8. ใช้โมเดลในการทำนายค่าล่วงหน้า
future_data = {
    'Time_delta': [df['Time_delta'].max() + 30],  # 30 วินาทีในอนาคต
    'Memory_Available': [1800],  # ตัวอย่างข้อมูล Memory ที่จะใช้ทำนายในอนาคต
    'Disk_Reads': [32],  # Disk Reads คาดการณ์
    'Disk_Writes': [26],  # Disk Writes คาดการณ์
    'Network_Bytes': [560000]  # Network Bytes คาดการณ์
}

# Convert to DataFrame
future_df = pd.DataFrame(future_data)

# ทำนาย % Processor Time ล่วงหน้า
future_pred = model.predict(future_df)
print(f'Predicted future % Processor Time: {future_pred[0]:.2f}')
