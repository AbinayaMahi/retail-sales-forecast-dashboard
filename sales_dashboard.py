import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="🛒 Retail Sales Forecast Dashboard", layout="wide")
st.title("Smart Retail Sales Forecast Dashboard")
st.markdown("Upload your forecast CSV to visualize predicted sales, stock, and expiry risk per product.")

uploaded_file = st.file_uploader("Upload your forecast CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")
    st.dataframe(df.head())

    # Ensure column names — try common variants and normalize
    # expected columns: Product_Name, Predicted_Sales (or Predicted_Sales_7d), Stock_Quantity, Expiry_Status
    # optional comparison columns: ARIMA_Pred, Prophet_Pred
    colmap = {c.lower(): c for c in df.columns}
    # normalize names if user uploaded different columns
    if "predicted_sales" not in df.columns and "predicted_sales_7d" in df.columns:
        df = df.rename(columns={"Predicted_Sales_7d": "Predicted_Sales"})
    if "Predicted_Sales" not in df.columns and "predicted_sales" in df.columns:
        df = df.rename(columns={colmap.get("predicted_sales"): "Predicted_Sales"})
    if "Stock_Quantity" not in df.columns and "stock_quantity" in colmap:
        df = df.rename(columns={colmap.get("stock_quantity"): "Stock_Quantity"})
    if "Expiry_Status" not in df.columns and "expiry_status" in colmap:
        df = df.rename(columns={colmap.get("expiry_status"): "Expiry_Status"})
    # final check
    required = ["Product_Name", "Predicted_Sales", "Stock_Quantity", "Expiry_Status"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Missing columns in CSV: {missing}. Please ensure these columns exist.")
    else:
        products = df["Product_Name"].unique().tolist()
        product = st.selectbox(" Select Product", products)
        product_data = df[df["Product_Name"] == product].iloc[0]

        # plot predicted vs stock
        predicted_sales = float(product_data["Predicted_Sales"])
        stock_quantity = float(product_data["Stock_Quantity"])
        fig, ax = plt.subplots(figsize=(6,4))
        bars = ax.bar(["Predicted Sales (7 Days)", "Current Stock"], [predicted_sales, stock_quantity], color=["skyblue","lightgreen"])
        ax.set_ylabel("Units")
        ax.set_title(f"Predicted Sales vs Stock for {product}")
        ax.bar_label(bars, fmt="%.0f", padding=3)
        st.pyplot(fig)

        # Expiry status
        expiry_status = str(product_data["Expiry_Status"])
        if "safe" in expiry_status.lower():
            st.success(f" Expiry Status: {expiry_status}")
        elif "unknown" in expiry_status.lower():
            st.warning(f" Expiry Status: {expiry_status}")
        else:
            st.error(f" Expiry Status: {expiry_status}")

        # Optional: model comparison if columns exist
        if "ARIMA_Pred" in df.columns and "Prophet_Pred" in df.columns:
            st.subheader(f"Model Comparison — {product}")
            days = list(range(1,8))
            arima_vals = df[df["Product_Name"]==product]["ARIMA_Pred"].values[:7]
            prophet_vals = df[df["Product_Name"]==product]["Prophet_Pred"].values[:7]
            plt.figure(figsize=(6,4))
            plt.plot(days, arima_vals, marker="o", label="ARIMA")
            plt.plot(days, prophet_vals, marker="o", label="Prophet")
            plt.xlabel("Days Ahead")
            plt.ylabel("Predicted Sales")
            plt.title(f"7-Day Forecast Comparison — {product}")
            plt.legend()
            plt.grid(alpha=0.4)
            st.pyplot(plt)

        st.subheader("📋 Product Summary")
        st.markdown(f"**Product:** {product}  \n**Predicted Sales (7d):** {predicted_sales:.2f}  \n**Stock Quantity:** {stock_quantity:.2f}  \n**Expiry Status:** {expiry_status}")
else:
    st.warning("Please upload your final forecast CSV file to continue.")
