import pandas as pd
import numpy as np
import csv 
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from sklearn.metrics import mean_absolute_error, mean_squared_error
import math
import tensorflow as tf
from sklearn.metrics import accuracy_score

def calculate_accuracy(y_true, y_pred):
    # แปลงค่าคาดการณ์และค่าจริงให้เป็น 0 หรือ 1 สำหรับการคำนวณความแม่นยำ
    y_true_binary = (y_true > 0.5).astype(int)
    y_pred_binary = (y_pred > 0.5).astype(int)
    return accuracy_score(y_true_binary, y_pred_binary)

class ResourcePredictor:
    def __init__(self, cpu_threshold, memory_threshold, disk_reads_threshold,
                 disk_writes_threshold, network_io_threshold):
        # Initialize thresholds for bottleneck detection
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_reads_threshold = disk_reads_threshold
        self.disk_writes_threshold = disk_writes_threshold
        self.network_io_threshold = network_io_threshold
        self.scaler = MinMaxScaler()
        self.model_anomaly = None
        self.model_lstm = None
        
    def read_csv(file_path):
        df = pd.read_csv(file_path)
        return df.to_dict(orient='list')

    def process_data(self, data, new_data):
        if not data or not new_data:
            raise ValueError("Data or new data cannot be empty.")

        df = pd.DataFrame(data)
        df_new = pd.DataFrame(new_data)
        df = pd.concat([df, df_new], ignore_index=True)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])

        normalized_data = self.scaler.fit_transform(df[['Processor(_Total) % Processor Time',
                                                        'Memory Available MBytes',
                                                        'PhysicalDisk(_Total) Disk Reads/sec',
                                                        'PhysicalDisk(_Total) Disk Writes/sec',
                                                        'Network Interface(eth0) Bytes Total/sec']])
        df_normalized = pd.DataFrame(normalized_data, columns=['Processor(_Total) % Processor Time',
                                                                'Memory Available MBytes',
                                                                'PhysicalDisk(_Total) Disk Reads/sec',
                                                                'PhysicalDisk(_Total) Disk Writes/sec',
                                                                'Network Interface(eth0) Bytes Total/sec'])

        # Anomaly Detection
        self.detect_anomalies(df_normalized, df)

        # Prepare LSTM data and train model
        X, y = self.prepare_lstm_data(normalized_data, window_size=5)
        if X.size == 0 or y.size == 0:
            raise ValueError("Insufficient data for training LSTM model.")
        self.train_lstm_model(X, y)

        # Predict next CPU usage
        next_cpu_normalized = self.predict_cpu_usage(X)[0][0]  # Get the normalized value
        next_cpu_prediction = self.scaler.inverse_transform([[next_cpu_normalized, 0, 0, 0, 0]])[0][0]

        recommendation = self.provide_recommendation(next_cpu_prediction, df_normalized.iloc[-1, 1])
        bottleneck_prediction = self.predict_bottleneck(next_cpu_prediction, df_normalized.iloc[-1, 1],
                                                        df_normalized.iloc[-1, 2], df_normalized.iloc[-1, 3],
                                                        df_normalized.iloc[-1, 4])
        return {"anomalies": df[df['Anomaly'] == 1], 
                "mae": self.mae,
                "mse": self.mse,
                "rmse": self.rmse,
                "accuracy": self.accuracy,  # เพิ่มการส่งคืนความแม่นยำ
                "next_cpu_prediction": next_cpu_prediction,
                "recommendation": recommendation,
                "bottleneck_prediction": bottleneck_prediction}
    
    def detect_anomalies(self, df_normalized, df):
        self.model_anomaly = IsolationForest(contamination=0.5)
        self.model_anomaly.fit(df_normalized)
        df['Anomaly'] = self.model_anomaly.predict(df_normalized)
        df['Anomaly'] = df['Anomaly'].map({1: 0, -1: 1})  # 1: Anomaly, 0: Normal

    def prepare_lstm_data(self, data, window_size):
        X, y = [], []
        for i in range(window_size, len(data)):
            X.append(data[i-window_size:i])
            y.append(data[i, 0])  # Predict CPU Usage
        return np.array(X), np.array(y)

    def train_lstm_model(self, X, y):
        X = np.reshape(X, (X.shape[0], X.shape[1], X.shape[2]))
        self.model_lstm = Sequential()
        self.model_lstm.add(Input(shape=(X.shape[1], X.shape[2])))
        self.model_lstm.add(LSTM(units=100, return_sequences=True))
        self.model_lstm.add(LSTM(units=100))
        self.model_lstm.add(Dense(1))
        self.model_lstm.compile(optimizer='adam', loss='mean_squared_error')
        if X.shape[0] > 1:
            history = self.model_lstm.fit(X, y, epochs=10, batch_size=2, validation_split=0.1, 
                                          callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)])
        else:
            history = self.model_lstm.fit(X, y, epochs=10, batch_size=1)

        y_pred = self.model_lstm.predict(X)
        self.mae = mean_absolute_error(y, y_pred)
        self.mse = mean_squared_error(y, y_pred)
        self.rmse = math.sqrt(self.mse)
        
        # คำนวณความแม่นยำ (accuracy) ในกรณีที่มีการแบ่งเป็น 0 หรือ 1
        self.accuracy = calculate_accuracy(y, y_pred)
    def predict_cpu_usage(self, X):
        last_sequence = X[-1].reshape(1, X.shape[1], X.shape[2])
        return self.model_lstm.predict(last_sequence)

    def provide_recommendation(self, cpu_usage, memory_available):
        cpu_usage = self.scaler.inverse_transform([[cpu_usage, 0, 0, 0, 0]])[0][0]
        memory_available = self.scaler.inverse_transform([[0, memory_available, 0, 0, 0]])[0][1]
        if cpu_usage > 80 and memory_available < 2000:
            return "Consider optimizing CPU-intensive operations and freeing up memory."
        elif cpu_usage > 80:
            return "CPU usage is high. Consider optimizing your code or scaling resources."
        elif memory_available < 2000:
            return "Low memory available. Free up memory or increase available resources."
        else:
            return "System performance is within acceptable limits."

    def predict_bottleneck(self, cpu_usage, memory_available, disk_reads, disk_writes, network_io):
        messages = []
        if cpu_usage > self.cpu_threshold:
            messages.append("Potential CPU bottleneck detected.")
        if memory_available < self.memory_threshold:
            messages.append("Potential memory bottleneck detected.")
        if disk_reads > self.disk_reads_threshold:
            messages.append("Potential disk read bottleneck detected.")
        if disk_writes > self.disk_writes_threshold:
            messages.append("Potential disk write bottleneck detected.")
        if network_io > self.network_io_threshold:
            messages.append("Potential network I/O bottleneck detected.")
        
        if not messages:
            return "No significant bottlenecks detected."
        return " ".join(messages)

# Example usage
if __name__ == "__main__":
    # Create instance of ResourcePredictor with default thresholds
    predictor = ResourcePredictor(cpu_threshold=85.0, memory_threshold=1500.0, disk_reads_threshold=40.0,
                 disk_writes_threshold=35.0, network_io_threshold=600000.0)

    # Example data
    data = {
    "Timestamp": [
        "09/10/2024 13:00:00", "09/10/2024 13:01:00", "09/10/2024 13:02:00", 
        "09/10/2024 13:03:00", "09/10/2024 13:04:00", "09/10/2024 13:05:00",
        "09/10/2024 13:06:00", "09/10/2024 13:07:00", "09/10/2024 13:08:00", 
        "09/10/2024 13:09:00", "09/10/2024 13:10:00", "09/10/2024 13:11:00",
        "09/10/2024 13:12:00", "09/10/2024 13:13:00", "09/10/2024 13:14:00"
    ],
    "Processor(_Total) % Processor Time": [
        10.5, 12.3, 14.8, 16.7, 18.4, 20.1, 
        22.5, 24.0, 26.1, 28.0, 30.2, 32.1, 
        34.0, 36.2, 38.1
    ],
    "Memory Available MBytes": [
        2048, 2000, 1950, 1900, 1850, 1800, 
        1750, 1700, 1650, 1600, 1550, 1500, 
        1450, 1400, 1350
    ],
    "PhysicalDisk(_Total) Disk Reads/sec": [
        30.0, 32.0, 34.0, 36.0, 38.0, 40.0, 
        42.0, 44.0, 46.0, 48.0, 50.0, 52.0, 
        54.0, 56.0, 58.0
    ],
    "PhysicalDisk(_Total) Disk Writes/sec": [
        20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 
        32.0, 34.0, 36.0, 38.0, 40.0, 42.0, 
        44.0, 46.0, 48.0
    ],
    "Network Interface(eth0) Bytes Total/sec": [
        500000, 510000, 520000, 530000, 540000, 550000, 
        560000, 570000, 580000, 590000, 600000, 610000, 
        620000, 630000, 640000
    ]
}
    
    new_data = {
        "Timestamp": ["09/10/2024 13:03:00", "09/10/2024 13:03:30"],
        "Processor(_Total) % Processor Time": [22.0, 24.5],
        "Memory Available MBytes": [1800, 1750],
        "PhysicalDisk(_Total) Disk Reads/sec": [28.0, 30.0],
        "PhysicalDisk(_Total) Disk Writes/sec": [26.0, 28.0],
        "Network Interface(eth0) Bytes Total/sec": [560000, 570000]
    }
    
    # Process data
    results = predictor.process_data(data, new_data)
    print("Anomalies Detected:\n", results["anomalies"])
    print(f"Mean Absolute Error (MAE): {results['mae']}")
    print(f"Mean Squared Error (MSE): {results['mse']}")
    print(f"Root Mean Squared Error (RMSE): {results['rmse']}")
    print(f"Accuracy: {results['accuracy']}")  # แสดงความแม่นยำ
    print("Next CPU Prediction:", results["next_cpu_prediction"])
    print("Recommendation:", results["recommendation"])
    print("Bottleneck Prediction:", results["bottleneck_prediction"])
