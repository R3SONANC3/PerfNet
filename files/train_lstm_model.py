import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import math

def create_input_sequence(data, look_back=3):
    X = []
    y = []
    for i in range(len(data) - look_back):
        X.append(data[i:(i + look_back), :])
        y.append(data[i + look_back, 0])  # สมมติว่าเราต้องการคาดการณ์ค่าของฟีเจอร์แรก
    return np.array(X), np.array(y)

def load_and_finetune_model(model_path, X, y, look_back=3):
    # โหลดโมเดลที่บันทึกไว้
    model = tf.keras.models.load_model(model_path)
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

    # Normalize data
    scaler_X = MinMaxScaler(feature_range=(0, 1))
    X_scaled = scaler_X.fit_transform(X)
    
    # สร้าง sequence และ normalize
    X_seq, y_seq = create_input_sequence(X_scaled, look_back)
    scaler_y = MinMaxScaler(feature_range=(0, 1))
    y_scaled = scaler_y.fit_transform(y_seq.reshape(-1, 1))

    # ฝึกโมเดลเพิ่มเติม
    history = model.fit(X_seq, y_scaled, epochs=10, batch_size=2, validation_split=0.1,
                        callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)])
    
    # Save the updated model
    model.save('models/saved_model.h5')
    
    # Evaluate the model
    y_pred = model.predict(X_seq)
    y_pred_rescaled = scaler_y.inverse_transform(y_pred).flatten()

    mae = mean_absolute_error(y_seq, y_pred_rescaled)
    mse = mean_squared_error(y_seq, y_pred_rescaled)
    rmse = math.sqrt(mse)
    
    return model, mae, mse, rmse

# Example usage
# Dummy data for illustration purposes
X = np.random.rand(100, 5)  # 100 samples, 5 features
y = np.random.rand(100)    # 100 target values

# Load and fine-tune the model
model_path = 'models/saved_model.h5'
model, mae, mse, rmse = load_and_finetune_model(model_path, X, y)

print("MAE:", mae)
print("MSE:", mse)
print("RMSE:", rmse)