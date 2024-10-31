import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error
import numpy as np
import matplotlib.pyplot as plt

# โหลดข้อมูล
data = pd.read_csv('data/processed/resource_usage_10000.csv')

# แปลงคอลัมน์ Timestamp เป็น datetime และแยกฟีเจอร์ที่ต้องการออกมา
data['Timestamp'] = pd.to_datetime(data['Timestamp'])
data['Hour'] = data['Timestamp'].dt.hour  # แยกชั่วโมง
data['Minute'] = data['Timestamp'].dt.minute  # แยกนาที
data['DayOfWeek'] = data['Timestamp'].dt.dayofweek  # แยกวันในสัปดาห์

# ลบคอลัมน์ Timestamp เนื่องจากเราได้แปลงข้อมูลที่จำเป็นออกมาแล้ว
data = data.drop(columns=['Timestamp'])

# แบ่งข้อมูลเป็น features และ target
X = data.drop(columns=['requet'])
y = data['requet']

# แบ่งข้อมูลเป็นชุดฝึกและชุดทดสอบ
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# สร้าง pipeline ที่รวมการ scaling และการฝึกโมเดล
pipeline = make_pipeline(StandardScaler(), LinearRegression())

# ฝึกโมเดลด้วย Cross-Validation
scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
print(f'Scaled Cross-Validation Mean Squared Error: {-np.mean(scores):.2f}')

# ฝึกโมเดลบนชุดฝึก
pipeline.fit(X_train, y_train)

# ทดสอบโมเดลบนชุดทดสอบ
y_pred = pipeline.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f'Scaled Test Mean Squared Error: {mse:.2f}')

# แสดงกราฟความผิดพลาด
plt.scatter(y_test, y_pred)
plt.xlabel('True Values')
plt.ylabel('Predictions')
plt.title('True Values vs Predictions')
plt.show()