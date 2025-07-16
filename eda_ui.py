# eda_ui.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Cargar modelo y label encoder
modelo = joblib.load("modelo_clasificador.pkl")
label_encoder = joblib.load("label_encoder.pkl")

def eda_ui():
    st.title("📊 Análisis Exploratorio de Datos Financieros")

    # Cargar dataset
    df = pd.read_csv("01_dataset_depurado.csv")

    # Selección de empresas
    empresas_disponibles = df["Ticker"].unique()
    empresas_sel = st.multiselect("Selecciona una o más empresas", sorted(empresas_disponibles), default=[empresas_disponibles[0]])
    df_empresas = df[df["Ticker"].isin(empresas_sel)]

    # Filtro por año
    año_sel = "Todos"
    if "Year" in df.columns:
        años = sorted(df["Year"].dropna().unique())
        año_sel = st.selectbox("Filtra por año (opcional)", ["Todos"] + años)
        if año_sel != "Todos":
            df_empresas = df_empresas[df_empresas["Year"] == año_sel]

    # Selección de métrica numérica
    numeric_cols = df_empresas.select_dtypes(include='number').columns
    if numeric_cols.empty:
        st.warning("⚠️ No hay columnas numéricas en el dataset.")
        return

    columna_metric = st.selectbox("Selecciona una métrica numérica para analizar", numeric_cols)

    # Gráfico de evolución temporal
    if len(empresas_sel) > 1 or año_sel == "Todos":
        st.subheader("📈 Comparación de evolución temporal")
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        sns.lineplot(data=df_empresas, x="Year", y=columna_metric, hue="Ticker", marker="o", ax=ax1)
        ax1.set_title(f"Evolución de {columna_metric}")
        st.pyplot(fig1)

    # Histograma (una empresa, varios años)
    if len(empresas_sel) == 1 and año_sel == "Todos":
        st.subheader("📊 Distribución histórica de la métrica seleccionada")
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        sns.histplot(df_empresas[columna_metric], kde=True, ax=ax2)
        ax2.set_title(f"Distribución de {columna_metric}")
        st.pyplot(fig2)

    # IA: análisis por clase si existe "Label"
    
    # Añadir predicción del modelo si no está ya incluida
    if "Label" not in df.columns:
        X = df[modelo.feature_names_in_].copy()
        X = X.fillna(0)
        predicciones = modelo.predict(X)
        df["Label"] = label_encoder.inverse_transform(predicciones)

    
    if "Label" in df.columns:
        st.markdown("---")
        st.header("🧠 Análisis por Clasificación del Modelo IA")

        # 📊 Distribución de clases
        st.subheader("Distribución de clases")
        st.bar_chart(df["Label"].value_counts())

        # 📈 Comparar métrica seleccionada por clase
        st.subheader(f"{columna_metric} medio por clase")
        promedio = df.groupby("Label")[columna_metric].mean().round(2)
        st.dataframe(promedio)

        # 📦 Boxplot
        st.subheader(f"Distribución de '{columna_metric}' por clase")
        fig3, ax3 = plt.subplots(figsize=(7, 4))
        sns.boxplot(data=df, x="Label", y=columna_metric, ax=ax3)
        st.pyplot(fig3)

    st.markdown("---")
    st.markdown("Creado para el TFM - Big Data e IA en Finanzas | by Luis Alonso")

# Para ejecución individual
if __name__ == "__main__":
    eda_ui()
