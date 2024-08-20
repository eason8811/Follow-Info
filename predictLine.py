import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import json

# 示例数据
with open('data.json', 'r') as f:
    data = json.loads(f.read())


# 创建DataFrame
df = pd.DataFrame(data)

# 创建多个滞后特征
for lag in range(1, 6):
    df[f'short_position_lag_{lag}'] = df['short_position'].shift(lag)

# 去除NaN值
df = df.dropna()

# 定义特征和标签
X = df[[f'short_position_lag_{lag}' for lag in range(1, 6)]]
y = df['close']

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 标准化数据
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 创建神经网络模型
model = Sequential()
model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(1))

# 编译模型
model.compile(optimizer='adam', loss='mean_squared_error')

# 训练模型
history = model.fit(X_train, y_train, epochs=100, batch_size=10, validation_split=0.2, verbose=0)

# 预测
y_pred_nn = model.predict(X_test)

# 评估模型
mse_nn = mean_squared_error(y_test, y_pred_nn)

# 可视化实际值和预测值
plt.figure(figsize=(10, 6))
plt.plot(y_test.values, label='Actual Close', marker='o')
plt.plot(y_pred_nn, label='Predicted Close (Neural Network)', marker='x')
plt.title('Actual vs Predicted Close Prices (Neural Network)')
plt.xlabel('Test Sample Index')
plt.ylabel('Close Price')
plt.legend()
plt.grid(True)
plt.show()

print(f'Mean Squared Error: {mse_nn}')


