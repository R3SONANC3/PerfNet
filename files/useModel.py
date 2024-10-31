import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import math

# โหลดโมเดลที่บันทึกไว้
model_path = 'models/saved_model.h5'
model = tf.keras.models.load_model(model_path)
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

# ข้อมูลทดสอบจริง (แทนที่ด้วยข้อมูลจริงของคุณ)
# สมมติว่าคุณมีข้อมูลจริงที่เป็น DataFrame เช่นนี้:
date_range_new = pd.date_range(start='2024-09-01', periods=20, freq='h')  # ข้อมูล 10 ชั่วโมง
# แทนที่ด้วยข้อมูลจริงของคุณ
real_data = np.array([
    [40, 5100, 9, 4, 980],
    [42, 5050, 10, 5, 1000],
    [43, 5000, 11, 6, 1050],
    [44, 4950, 12, 5, 1100],
    [45, 4900, 13, 4, 1150],
    [46, 4850, 14, 3, 1200],
    [47, 4800, 15, 5, 1250],
    [48, 4750, 16, 6, 1300],
    [49, 4700, 17, 7, 1350],
    [50, 4650, 18, 8, 1400],
    [51, 4600, 19, 9, 1450],
    [52, 4550, 20, 10, 1500],
    [53, 4500, 21, 11, 1550],
    [54, 4450, 22, 12, 1600],
    [55, 4400, 23, 13, 1650],
    [56, 4350, 24, 14, 1700],
    [57, 4300, 25, 15, 1750],
    [58, 4250, 26, 16, 1800],
    [59, 4200, 27, 17, 1850],
    [60, 4150, 28, 18, 1900],  # ข้อมูลถึงเวลาที่ 20 ชั่วโมง
])

# โหลดข้อมูลจริงเข้า DataFrame
real_data_df = pd.DataFrame(real_data, columns=['CPU_Usage', 'Memory_Available_MB', 
                                                'Disk_Reads_per_sec', 'Disk_Writes_per_sec', 
                                                'Network_Bytes_Total_per_sec'], index=date_range_new)

# เตรียมข้อมูลสำหรับการทำนาย
scaler_X = MinMaxScaler(feature_range=(0, 1))
scaler_X.fit(real_data_df)  # ฟิต scaler กับข้อมูลจริง
new_scaled_data = scaler_X.transform(real_data_df)

look_back = 3
def create_input_sequence(data, look_back=3):
    X = []
    for i in range(len(data) - look_back):
        X.append(data[i:(i + look_back), :])
    return np.array(X)

X_new = create_input_sequence(new_scaled_data, look_back)

# ทำการทำนายข้อมูลจริง
if X_new.shape[0] > 0:  # ตรวจสอบว่ามีข้อมูลพอให้ทำนายหรือไม่
    predictions = model.predict(X_new)

    # ทำการ inverse normalization เพื่อแปลงผลลัพธ์กลับสู่รูปแบบดั้งเดิม
    predictions_rescaled = scaler_X.inverse_transform(
        np.concatenate([predictions, np.zeros((predictions.shape[0], new_scaled_data.shape[1] - 1))], axis=1)
    )[:, 0]

    print("Predicted CPU Usage:", predictions_rescaled)

    # ข้อมูลจริงสำหรับทดสอบ
    y_true = real_data_df['CPU_Usage'].values[look_back:]  # ใช้ข้อมูลจริงหลังจาก look_back

    # คำนวณค่าความแม่นยำ
    mae = mean_absolute_error(y_true, predictions_rescaled)
    mse = mean_squared_error(y_true, predictions_rescaled)
    rmse = math.sqrt(mse)

    print(f"Mean Absolute Error (MAE): {mae}")
    print(f"Mean Squared Error (MSE): {mse}")
    print(f"Root Mean Squared Error (RMSE): {rmse}")
else:
    print("Not enough data to make predictions.")