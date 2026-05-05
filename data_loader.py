import pandas as pd
import numpy as np
import streamlit as st


REGION_COORDS = {
    "North":   {"lat": 43.0, "lon": -85.0},
    "South":   {"lat": 30.0, "lon": -90.0},
    "East":    {"lat": 40.7, "lon": -74.0},
    "West":    {"lat": 37.8, "lon": -120.5},
    "Central": {"lat": 41.8, "lon": -93.0},
}

@st.cache_data(show_spinner="Cargando datos...")
def cargar_datos(ruta="data/retail_sales.csv"):
    df = pd.read_csv(ruta, parse_dates=["Date"])
    df = df[~df["Category"].astype(str).str.strip()
              .isin(["NaN?", "nan", "NaN", ""])]
    df = df.dropna(subset=["Category"])

    df = df.dropna(subset=["Sales", "Profit","Quantity","Date","Region"])

    df = df[df["Sales"] >= 0]
    df = df[df["Profit"] >=0]
    df = df[df["Quantity"] >= 0]

    df["Category"] = df["Category"].astype(str).str.title().str.strip()
    df["Region"] = df["Region"].astype(str).str.title().str.strip()

    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["Year"] = df["Date"].dt.year.astype(str)

    df["Profit_Margin"] = (df["Profit"] / df["Sales"])*100

    df = df.reset_index(drop=True)
    return df