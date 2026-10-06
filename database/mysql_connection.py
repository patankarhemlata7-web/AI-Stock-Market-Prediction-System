from sqlalchemy import create_engine

DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_NAME = "stock_market_project"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)