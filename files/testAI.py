from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import joblib

# โหลดโมเดลและ scaler
model = joblib.load('models/linear_regression_model.pkl')
scaler = joblib.load('models/scaler.pkl')

# สร้าง DataFrame จากข้อมูลที่มี
data = pd.read_csv('data/processed/resource_usage_10000.csv')

# เตรียมข้อมูลสำหรับการฝึก
X = data[['Processor(_Total) % Processor Time', 
          'Memory Available MBytes', 
          'PhysicalDisk(_Total) Disk Reads/sec', 
          'PhysicalDisk(_Total) Disk Writes/sec', 
          'Network Interface(eth0) Bytes Total/sec']]
y = data['request']

# ทำ Scaling ข้อมูล
X_scaled = scaler.fit_transform(X)

# สร้างโมเดลใหม่สำหรับการคาดการณ์ค่าฟีเจอร์จาก request
model_feature = LinearRegression()
model_feature.fit(y.values.reshape(-1, 1), X_scaled)

# ฟังก์ชันสำหรับคาดการณ์ค่าฟีเจอร์จาก request
def predict_features(request_value):
    # สร้าง DataFrame สำหรับ input ใหม่
    request_df = pd.DataFrame([[request_value]], columns=['request'])
    request_scaled = scaler.transform(request_df)
    
    # ทำนายค่าฟีเจอร์จาก request ที่ปรับค่าแล้ว
    predictions = model_feature.predict(request_scaled)
    
    # สร้าง DataFrame จากผลลัพธ์
    predicted_features = pd.DataFrame(predictions, columns=X.columns)
    
    return predicted_features

# ทำนายค่าฟีเจอร์สำหรับ request ที่กำหนด
request_value = 10000
predicted_features = predict_features(request_value)

print(f'Predicted features for request = {request_value}:')
print(predicted_features)