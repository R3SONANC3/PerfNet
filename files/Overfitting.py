from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np
import pandas as pd

# โหลดข้อมูล
data = pd.read_csv('data/processed/resource_usage_10000.csv')

# แบ่งข้อมูลเป็น features และ target
X = data.drop(columns=['requet'])
y = data['requet']

# แบ่งข้อมูลเป็นชุดฝึกและชุดทดสอบ
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# สร้างโมเดล
model = LinearRegression()

# ฝึกโมเดลด้วย Cross-Validation
scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
print(f'Cross-Validation Mean Squared Error: {-np.mean(scores):.2f}')

# ฝึกโมเดลบนชุดฝึก
model.fit(X_train, y_train)

# ทดสอบโมเดลบนชุดทดสอบ
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f'Test Mean Squared Error: {mse:.2f}')