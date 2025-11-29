import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA (Opcional, pero da buen estilo) ---
st.set_page_config(page_title="Delivery Dashboard", layout="wide")

# --- 1. CARGA DE DATOS ---
@st.cache_data # Esto ayuda a que la página no recargue el CSV cada vez que tocas un botón
def load_data():
    # Asegúrate de usar el nombre correcto de tu archivo
    df = pd.read_csv("Food_Delivery_Route_Efficiency_Dataset.csv")
    return df

df = load_data()

# --- TÍTULO Y DESCRIPCIÓN ---
# Elemento 1: st.title
st.title(" 🛵 Dashboard de Eficiencia de Envíos")
# Elemento 2: st.markdown
st.markdown("Este tablero analiza los tiempos de entrega según el **clima**, **tráfico** y **vehículo**.")

# --- BARRA LATERAL (SIDEBAR) PARA FILTROS ---
# Elemento 3: st.sidebar
with st.sidebar:
    # Elemento 4: st.header
    st.header("🎛️ Filtros Globales")
    
    # Elemento 5: st.radio (Filtrar por Nivel de Tráfico)
    trafico_filter = st.radio(
        "Nivel de Tráfico:",
        options=["Todos", "Low", "Medium", "High"],
        index=0
    )
    
    # Elemento 6: st.slider (Filtrar por Distancia)
    distancia_min, distancia_max = int(df['distance_km'].min()), int(df['distance_km'].max())
    dist_range = st.slider(
        "Rango de Distancia (km):",
        min_value=distancia_min,
        max_value=distancia_max,
        value=(distancia_min, distancia_max)
    )
    if dist_range[0] == dist_range[1]:
        st.warning("⚠️ Por favor selecciona un rango de distancia válido (el inicio y el fin no pueden ser iguales).")
        st.stop() # Esto detiene la ejecución aquí y evita que los gráficos de abajo fallen.
    # Elemento 7: st.multiselect (Filtrar por Vehículo)
    vehiculos_disponibles = df['delivery_mode'].unique()
    vehiculos_sel = st.multiselect(
        "Selecciona Vehículos:",
        options=vehiculos_disponibles,
        default=vehiculos_disponibles
    )

    st.info("Ajusta los filtros para actualizar los gráficos.")

# --- APLICAR FILTROS AL DATAFRAME ---
df_filtered = df.copy()

# Filtro de Tráfico
if trafico_filter != "Todos":
    df_filtered = df_filtered[df_filtered['traffic_level'] == trafico_filter]

# Filtro de Distancia
df_filtered = df_filtered[
    (df_filtered['distance_km'] >= dist_range[0]) & 
    (df_filtered['distance_km'] <= dist_range[1])
]

# Filtro de Vehículo
if vehiculos_sel:
    df_filtered = df_filtered[df_filtered['delivery_mode'].isin(vehiculos_sel)]

# --- ESTRUCTURA DE PESTAÑAS ---
# Elemento 8: st.tabs
tab1, tab2, tab3 = st.tabs(["📊 Visión General", "🚀 Análisis de Flota", "📍 Rutas y Zonas"])

# === PESTAÑA 1: VISIÓN GENERAL ===
with tab1:
    st.subheader("Métricas Clave")
    
    # Elemento 9: st.metric (KPIs)
    col1, col2, col3 = st.columns(3)
    avg_time = df_filtered['delivery_time_min'].mean()
    total_orders = len(df_filtered)
    
    col1.metric("Total de Órdenes", total_orders)
    col2.metric("Tiempo Promedio (min)", f"{avg_time:.2f} min")
    col3.metric("Distancia Promedio", f"{df_filtered['distance_km'].mean():.2f} km")
    
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        st.write("##### Distribución por Clima (Pie Chart)")
        # GRÁFICO 1: PIE CHART
        if not df_filtered.empty:
            weather_counts = df_filtered['weather'].value_counts()
            
            fig1, ax1 = plt.subplots()
            ax1.pie(weather_counts, labels=weather_counts.index, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')  # Para que sea un círculo perfecto
            st.pyplot(fig1)
        else:
            st.warning("No hay datos para mostrar.")

    with col_graph2:
        st.write("##### Histograma de Tiempos de Entrega")
        # GRÁFICO 2: HISTOGRAMA
        fig2, ax2 = plt.subplots()
        ax2.hist(df_filtered['delivery_time_min'], bins=15, color='skyblue', edgecolor='black')
        ax2.set_xlabel("Minutos")
        ax2.set_ylabel("Frecuencia")
        st.pyplot(fig2)

# === PESTAÑA 2: ANÁLISIS DE FLOTA ===
with tab2:
    st.subheader("Rendimiento por Tipo de Vehículo")
    
    # Elemento 10: st.selectbox (Elegir qué variable comparar)
    variable_a_comparar = st.selectbox(
        "¿Qué quieres comparar?",
        ["Tiempo de Entrega (min)", "Distancia Recorrida (km)"]
    )
    
    col_mapping = {
        "Tiempo de Entrega (min)": "delivery_time_min",
        "Distancia Recorrida (km)": "distance_km"
    }
    col_name = col_mapping[variable_a_comparar]
    
    # Agrupar datos
    df_grouped = df_filtered.groupby('delivery_mode')[col_name].mean().sort_values()
    
    # GRÁFICO 3: BAR PLOT
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    df_grouped.plot(kind='bar', color='orange', ax=ax3)
    ax3.set_ylabel("Promedio")
    ax3.set_title(f"Promedio de {variable_a_comparar} por Vehículo")
    plt.xticks(rotation=45)
    st.pyplot(fig3)
    
    # Elemento 11: st.expander con st.dataframe
    with st.expander("Ver datos detallados de la flota"):
        st.dataframe(df_grouped)

# === PESTAÑA 3: RUTAS Y ZONAS ===
with tab3:
    st.subheader("Relación Distancia vs. Tiempo")
    
    # GRÁFICO 4: SCATTER PLOT
    # Colorear por nivel de tráfico
    colors = {'Low': 'green', 'Medium': 'yellow', 'High': 'red'}
    
    fig4, ax4 = plt.subplots(figsize=(8, 6))
    
    # Hacemos el scatter
    for traffic, color in colors.items():
        subset = df_filtered[df_filtered['traffic_level'] == traffic]
        ax4.scatter(subset['distance_km'], subset['delivery_time_min'], 
                    c=color, label=traffic, alpha=0.6, edgecolors='w')
    
    ax4.set_xlabel("Distancia (km)")
    ax4.set_ylabel("Tiempo de Entrega (min)")
    ax4.legend(title="Tráfico")
    ax4.grid(True, linestyle='--', alpha=0.5)
    
    st.pyplot(fig4)
    
    st.divider()
    
    # Elemento 12: st.button
    if st.button("🎲 Mostrar una orden aleatoria"):
        random_order = df.sample(1).iloc[0]
        st.success(f"Orden #{random_order['order_id']}: De {random_order['restaurant_zone']} a {random_order['customer_zone']} en {random_order['delivery_mode']}.")
