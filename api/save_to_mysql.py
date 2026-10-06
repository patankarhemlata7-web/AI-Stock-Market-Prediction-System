from api.stock_api import fetch_stock_data
from database.mysql_connection import engine

df = fetch_stock_data()

print(df.head())

df.to_sql(
    "stock_data",
    con=engine,
   if_exists="append",
    index=False
)
print("Min Date:", df["date"].min())
print("Max Date:", df["date"].max())
print("Data Saved Successfully")