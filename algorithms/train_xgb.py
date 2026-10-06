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

from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from database.mysql_connection import engine

# ======================================
# LOAD DATA
# ======================================

df = pd.read_sql(
    "SELECT * FROM stock_data",
    con=engine
)

# ======================================
# PREPROCESSING
# ======================================

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

# ======================================
# CREATE 30-DAY TARGET
# ======================================

df["target"] = df["close"].shift(-30)

# Remove last 30 rows with null target
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
# XGBOOST MODEL
# ======================================

model = XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)

model.fit(
    X_train,
    y_train
)

# ======================================
# EVALUATION
# ======================================

pred = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    pred
)

r2 = r2_score(
    y_test,
    pred
)

print("\n===== XGBOOST RESULTS =====")
print("Prediction Period : 30 Days")
print(f"MAE : {mae:.2f}")
print(f"R² Score : {r2:.4f}")
print("===========================")

# ======================================
# SAVE MODEL
# ======================================

os.makedirs(
    "models",
    exist_ok=True
)

joblib.dump(
    model,
    "models/xgb_model_30days.pkl"
)

print("✅ 30-Day XGBoost Model Saved")

# ======================================
# SAMPLE PREDICTION
# ======================================

future_price = model.predict(
    X.iloc[[-1]]
)[0]

print(f"\nPredicted Price After 30 Days: ₹{future_price:.2f}")