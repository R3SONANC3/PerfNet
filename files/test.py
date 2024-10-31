from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import joblib

# โหลดข้อมูล
data = pd.read_csv('data/processed/resource_usage_10000.csv')

# เตรียมข้อมูลสำหรับการฝึก
X = data[['Processor(_Total) % Processor Time', 
          'Memory Available MBytes', 
          'PhysicalDisk(_Total) Disk Reads/sec', 
          'PhysicalDisk(_Total) Disk Writes/sec', 
          'Network Interface(eth0) Bytes Total/sec']]
y = data['request']

# ทำ Scaling ข้อมูล
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# แบ่งข้อมูลเป็น Train/Test
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# สร้างและฝึกโมเดล
model = LinearRegression()
model.fit(X_train, y_train)

# บันทึกโมเดลและ scaler
joblib.dump(model, 'models/linear_regression_model.pkl')
joblib.dump(scaler, 'models/scaler.pkl')