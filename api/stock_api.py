import yfinance as yf
import pandas as pd


def fetch_stock_data():

    companies = {

    # NSE
    "Reliance_NSE": ("RELIANCE.NS", "NSE"),
    "TCS_NSE": ("TCS.NS", "NSE"),
    "Infosys_NSE": ("INFY.NS", "NSE"),
    "HDFC_NSE": ("HDFCBANK.NS", "NSE"),
    "Wipro_NSE": ("WIPRO.NS", "NSE"),
    "ICICI_NSE": ("ICICIBANK.NS", "NSE"),
    "SBI_NSE": ("SBIN.NS", "NSE"),
    "Axis_NSE": ("AXISBANK.NS", "NSE"),
    "LT_NSE": ("LT.NS", "NSE"),
    "ITC_NSE": ("ITC.NS", "NSE"),

    # BSE
    "Reliance_BSE": ("RELIANCE.BO", "BSE"),
    "TCS_BSE": ("TCS.BO", "BSE"),
    "Infosys_BSE": ("INFY.BO", "BSE"),
    "HDFC_BSE": ("HDFCBANK.BO", "BSE"),
    "Wipro_BSE": ("WIPRO.BO", "BSE"),
    "ICICI_BSE": ("ICICIBANK.BO", "BSE"),
    "SBI_BSE": ("SBIN.BO", "BSE"),
    "Axis_BSE": ("AXISBANK.BO", "BSE"),
    "LT_BSE": ("LT.BO", "BSE"),
    "ITC_BSE": ("ITC.BO", "BSE")
}
    
    all_data = []

    for company, (symbol, exchange) in companies.items():

        try:

            print(f"Downloading {company}...")

            df = yf.download(
                symbol,
                period="1d",
                interval="5m",
                auto_adjust=False,
                progress=False
            )

            if df.empty:
                continue

            df = df.reset_index()

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if "Datetime" in df.columns:
                time_col = "Datetime"
            else:
                time_col = "Date"

            df = df[
                [time_col, "Open", "High", "Low", "Close", "Volume"]
            ]

            df.columns = [
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]

            df["company"] = company
            df["exchange"] = exchange

            all_data.append(df)

        except Exception as e:
            print(f"Error: {e}")

    if len(all_data) == 0:
        return pd.DataFrame()

    final_df = pd.concat(
        all_data,
        ignore_index=True
    )

    final_df.columns = (
        final_df.columns
        .astype(str)
        .str.lower()
        .str.strip()
    )

    final_df = final_df.loc[
        :,
        ~final_df.columns.duplicated()
    ]

    return final_df


if __name__ == "__main__":

    df = fetch_stock_data()

    print(df.head())
    print("\nRows:", len(df))