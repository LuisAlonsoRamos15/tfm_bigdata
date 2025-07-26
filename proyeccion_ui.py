import streamlit as st
import pandas as pd
import yfinance as yf

def proyeccion_financiera_ui():
    st.set_page_config(page_title="Proyección Financiera", layout="wide")
    st.title("📈 Dashboard de Valoración de Empresas")

    # --- Cargar dataset directamente ---
    df = pd.read_csv("01_dataset_depurado.csv")

    # Obtener último año de EPS por empresa
    df_eps = df.sort_values("Year").groupby("Ticker").last().reset_index()
    df_eps = df_eps[["Ticker", "Diluted EPS_2_Key Ratios"]].rename(columns={"Diluted EPS_2_Key Ratios": "EPS_forward"})

    # Selección de empresa
    st.subheader("Paso 1: Selecciona una empresa del dataset")
    empresa = st.selectbox("Ticker disponible", df_eps["Ticker"].unique())

    if empresa:
        # Obtener precio actual con yfinance
        st.subheader("Paso 2: Precio actual de mercado")
        st.info("Esto puede tardar unos segundos...")

        def obtener_precio_actual(ticker):
            try:
                return yf.Ticker(ticker).info.get("currentPrice")
            except:
                return None

        df_eps["Precio_actual"] = df_eps["Ticker"].apply(obtener_precio_actual)
        df_eps = df_eps.dropna(subset=["EPS_forward", "Precio_actual"])

        fila = df_eps[df_eps["Ticker"] == empresa].iloc[0]
        eps_base = fila["EPS_forward"]
        precio_actual = fila["Precio_actual"]

        # Parámetros de usuario
        st.subheader("Paso 3: Parámetros de proyección")
        col1, col2, col3 = st.columns(3)
        with col1:
            g = st.slider("Tasa de crecimiento EPS anual (%)", 0.0, 30.0, 10.0) / 100
        with col2:
            per_objetivo = st.number_input("PER objetivo", value=18.0)
        with col3:
            anios = st.slider("Años a proyectar", 1, 10, 5)

        # Proyección a futuro
        resultados = []
        for n in range(1, anios + 1):
            eps_n = eps_base * (1 + g) ** n
            precio_n = eps_n * per_objetivo
            cagr = (precio_n / precio_actual) ** (1 / n) - 1
            resultados.append({
                "Año": f"{2024 + n}E",
                "EPS estimado": round(eps_n, 2),
                "Precio estimado": round(precio_n, 2),
                "CAGR esperado (%)": round(cagr * 100, 2)
            })

        df_resultados = pd.DataFrame(resultados)

        # Mostrar resumen
        st.subheader(f"Proyección para {empresa}")
        st.metric("EPS actual", round(eps_base, 2))
        st.metric("Precio actual", f"{precio_actual:.2f} $")

        st.dataframe(df_resultados, use_container_width=True)

        # Gráfico
        st.subheader("Evolución de precio estimado")
        st.line_chart(df_resultados.set_index("Año")["Precio estimado"])

    else:
        st.warning("Selecciona una empresa del dataset para continuar.")
