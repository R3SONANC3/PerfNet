import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# ตรวจสอบและสร้างโฟลเดอร์สำหรับบันทึกโมเดล
model_dir = 'models/'
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

# ตัวอย่างการฝึกและบันทึกโมเดล LSTM (ตามที่ทำในคำถามก่อนหน้า)
# 1. สร้างข้อมูลสุ่มสำหรับทดสอบ
date_range = pd.date_range(start='2024-01-01', periods=1000, freq='h')
np.random.seed(42) 
cpu_usage = np.random.uniform(low=20, high=80, size=(1000, 1))  
memory_available = np.random.uniform(low=1000, high=8000, size=(1000, 1))  
disk_reads = np.random.uniform(low=0, high=100, size=(1000, 1))  
disk_writes = np.random.uniform(low=0, high=100, size=(1000, 1))  
network_bytes = np.random.uniform(low=0, high=1000, size=(1000, 1))  

data = pd.DataFrame(
    data=np.hstack([cpu_usage, memory_available, disk_reads, disk_writes, network_bytes]), 
    columns=['CPU_Usage', 'Memory_Available_MB', 'Disk_Reads_per_sec', 'Disk_Writes_per_sec', 'Network_Bytes_Total_per_sec'],
    index=date_range
)
data.to_csv('data/processed/resource_usage.csv')

# 2. เตรียมข้อมูลสำหรับการฝึกโมเดล
data = pd.read_csv('data/processed/resource_usage.csv', parse_dates=['Unnamed: 0'], index_col='Unnamed: 0')
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

def create_dataset(data, look_back=3):
    X, y = [], []
    for i in range(len(data) - look_back):
        X.append(data[i:(i + look_back), :])
        y.append(data[i + look_back, 0])  
    return np.array(X), np.array(y)

look_back = 3
X, y = create_dataset(scaled_data, look_back)

train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# 3. สร้างโมเดล LSTM
model = Sequential()
model.add(LSTM(100, return_sequences=True, input_shape=(look_back, X.shape[2])))
model.add(LSTM(100))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mean_squared_error')

# 4. ฝึกโมเดล
history = model.fit(X_train, y_train, epochs=20, batch_size=16, validation_split=0.1, 
                    callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)])

# 5. ทำนายข้อมูลทดสอบ
y_pred = model.predict(X_test)

# 6. คำนวณ RMSE เพื่อประเมินความแม่นยำของโมเดล
y_test_rescaled = scaler.inverse_transform(
    np.concatenate([y_test.reshape(-1, 1), np.zeros((y_test.shape[0], data.shape[1] - 1))], axis=1))[:, 0]
y_pred_rescaled = scaler.inverse_transform(
    np.concatenate([y_pred, np.zeros((y_pred.shape[0], data.shape[1] - 1))], axis=1))[:, 0]

rmse = np.sqrt(np.mean((y_pred_rescaled - y_test_rescaled) ** 2))
print(f'Root Mean Squared Error (RMSE): {rmse}')

# 7. แสดงกราฟการทำนาย
plt.figure(figsize=(14, 7))
plt.plot(data.index[-len(y_test_rescaled):], y_test_rescaled, label='Actual CPU Usage')
plt.plot(data.index[-len(y_pred_rescaled):], y_pred_rescaled, label='Predicted CPU Usage')
plt.title('CPU Usage Prediction')
plt.xlabel('Timestamp')
plt.ylabel('CPU Usage (%)')
plt.legend()
plt.show()

# 8. บันทึกโมเดล
try:
    model_path = os.path.join(model_dir, 'saved_model.h5')
    model.save(model_path)
    print(f'Model saved at {model_path}')
except Exception as e:
    print(f"Error saving the model: {e}")