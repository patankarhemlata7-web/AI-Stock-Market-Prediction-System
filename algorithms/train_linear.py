import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

import pandas as pd
import joblib

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from database.mysql_connection import engine

# ======================================
# LOAD DATA FROM MYSQL
# ======================================

print("Loading stock data from MySQL...")

df = pd.read_sql(
    "SELECT * FROM stock_data",
    con=engine
)

# ======================================
# DATA PREPROCESSING
# ======================================

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values("date")

# ======================================
# CREATE 1 MONTH TARGET
# ======================================
# Assuming daily stock data
# 30 days ahead prediction

df["target"] = df["close"].shift(-30)

# Remove rows with missing target
df = df.dropna()

# ======================================
# FEATURES & TARGET
# ======================================

X = df[
    [
        "open",
        "high",
        "low",
        "volume"
    ]
]

y = df["target"]

print(f"Dataset Shape : {df.shape}")
print(f"Features Shape : {X.shape}")

# ======================================
# TRAIN TEST SPLIT
# ======================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# ======================================
# TRAIN MODEL
# ======================================

print("\nTraining Linear Regression Model...")

model = LinearRegression()

model.fit(
    X_train,
    y_train
)

# ======================================
# PREDICTION
# ======================================

y_pred = model.predict(X_test)

# ======================================
# EVALUATION
# ======================================

mae = mean_absolute_error(
    y_test,
    y_pred
)

mse = mean_squared_error(
    y_test,
    y_pred
)

rmse = mse ** 0.5

r2 = r2_score(
    y_test,
    y_pred
)

print("\n========== MODEL RESULTS ==========")
print(f"Prediction Period : 1 Month (30 Days)")
print(f"MAE  : {mae:.2f}")
print(f"MSE  : {mse:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R²   : {r2:.4f}")
print("===================================")

# ======================================
# SAVE MODEL
# ======================================

os.makedirs(
    "models",
    exist_ok=True
)

model_path = "models/linear_model_1month.pkl"

joblib.dump(
    model,
    model_path
)

print(f"\n✅ Model Saved Successfully")
print(f"📁 Location : {model_path}")

# ======================================
# SAMPLE PREDICTION
# ======================================

sample_data = X.iloc[[-1]]

future_price = model.predict(sample_data)[0]

print("\n========== SAMPLE FORECAST ==========")
print(f"Current Close Price : ₹{df['close'].iloc[-1]:.2f}")
print(f"Predicted Price After 30 Days : ₹{future_price:.2f}")
print("====================================")