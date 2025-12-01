import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Delivery Dashboard", layout="wide") #st.set_page_config sirve para congifurar los ajustes del la página, por ej: page_title (cambia el título que se ve en la pestaña del navegador)
#'layout="wide" sirve para usar todo el espacio en pantalla

df = pd.read_csv("Food_Delivery_Route_Efficiency_Dataset.csv")

st.title("Dashboard de Operaciones de Delivery") #st.title sirve para crear el título de la página. El título se verá en cada tab de la página
st.subheader("Análisis de tiempos, rutas y vehículos.") #st.subheader es para crear un subtítulo de la página

with st.sidebar: #st.sidebar crea un desplegable al lado izquierdo, en el cual vamos a asignar opciones de filtrado (todo lo que está indentado, va dentro del sidebar)
    st.header("Filtros Globales")
    
    trafico_filter = st.multiselect(
        "Nivel de Tráfico:",
        options=["Low", "Medium", "High"],
        default=["Low", "Medium", "High"]
    ) #st.multiselect crea un componente de selección múltiple
    
    min_dist, max_dist = int(df['distance_km'].min()), int(df['distance_km'].max()) #Desiganmos los valores de distancia min y máx a 2 variables (min_dist y max_dist)
    dist_range = st.slider(
        "Rango de Distancia (km):",
        min_value=min_dist,
        max_value=max_dist,
        value=(min_dist, max_dist)
    ) #Creamos el componente de barra deslizante, el cual va desde 0 a 12 (km)
    
    if dist_range[0] == dist_range[1]:
        st.warning("El inicio y fin del rango no pueden ser iguales.")
        st.stop() #En caso de que dist_range[0] == dist_range[1], la página nos va a avisar y no va a seguir intentando crear los gráficos, para evitar errores

    st.info("Filtra los datos para actualizar todos los gráficos.") #Crea una cajita con texto (de uso informativo para el usuario)

df_filtered = df[
    (df['traffic_level'].isin(trafico_filter)) &
    (df['distance_km'] >= dist_range[0]) &
    (df['distance_km'] <= dist_range[1])
] #Se crea un DataFrame filtrado, utilizando solo los datos que cumplen con los requisitos, en este caso son: pertenecer a los 'niveles de tráfico' que se solicitan, y que estén dentro del rango [dist_range[0], dist_range[1]]

tab1, tab2, tab3 = st.tabs(["Visión General", "Vehículos", "Zonas y Rutas"]) #Se crean las 'tabs' las cuales son una especie de 'pestañas', para tener mayor orden en la página

with tab1: #Esto sirve para trabajar dentro de la 'tab1'
    c1, c2, c3 = st.columns(3) #Separamos parte de la tab1 en 3 columnas ('c1','c2' y 'c3')
    c1.metric("Total Ordenes", len(df_filtered)) #Cantidad de Ordenes con los filtros que hayamos seleccionado (el largo de nuestro df_filtered)
    c2.metric("Tiempo Promedio", f"{df_filtered['delivery_time_min'].mean():.1f} min") #Promedio de Tiempo en el que se demora un pedido en llegar a su destino, dentro de los filtros seleccionados
    c3.metric("Distancia Promedio", f"{df_filtered['distance_km'].mean():.1f} km") #Promedio de Distancia que recorren los pedidos, dentro de los filtros seleccionados
    
    st.divider() #Crea una línea divisora en el tab1
    
    col_izq, col_der = st.columns(2) #Separamos parte de la tab1 en 2 columnas ('col_izq' y 'col_der')
    
    with col_izq: #Trabajando dentro de la columna izquierda
        st.subheader("Popularidad de Vehículos") #Subtítulo de la columna
        if not df_filtered.empty: #Esto es una medida para evitar errores, ya que pasa por un filtro, si es que df_filteres NO está vacío, ejecute el siguiente código
            counts = df_filtered['delivery_mode'].value_counts() #Cuenta la cantidad de Vehículos según los filtros seleccionados
            
            fig1, ax1 = plt.subplots() #fig es donde se guarda la figura, y ax es cómo llamamos y donde mandamos los comandos
            ax1.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90, #.pie crea el gráfico de torta
                    colors=['#ff9999','#66b3ff','#99ff99','#ffcc99']) #autopct sirve para calcular y escribir el porcentaje que representa cada pedazo de la torta
            st.pyplot(fig1) #Muestra la figura 'fig1'
            with st.expander("Ver datos detallados de la flota"):
                st.dataframe(counts)
        else: #En caso de que df_filtered SI esté vacío, lanzará un aviso de que no hay datos disponibles
            st.info("No hay datos disponibles.")

    with col_der: #Trabajando dentro de la columna derecha
        st.subheader("Tiempo Promedio según el Clima")
        if not df_filtered.empty: #Si es que df_filtered NO está vacía, se ejecuta el código que sigue
            df_weather = df_filtered.groupby('weather')['delivery_time_min'].mean().sort_values() #Agrupamos por clima y sacamos promedio del tiempo
            
            fig2, ax2 = plt.subplots()
            ax2.barh(df_weather.index, df_weather.values, color='teal') #.barh crea el gráfico de barra horizontal, .index son las etiquetas (clima) y .values son los números (minutos de delivery)
            ax2.set_xlabel("Minutos Promedio")
            st.pyplot(fig2)
            with st.expander("Ver datos detallados de la flota"):
                st.dataframe(df_weather)
    

with tab2: #Trabajando dentro del tab2
    st.subheader("Rendimiento por Vehículo en Zonas Específicas")
    
    zonas = df['restaurant_zone'].unique() #.unique sirve para dejar una sola instancia con cada nombre diferente en la columna 'restaurant_zone' del DataFrame y los guarda en 'zonas'
    zona_sel = st.selectbox("Selecciona la Zona del Restaurante:", zonas) #.selectbox crea una caja con diferentes opciones, en este caso se toma las opciones de la variable 'zonas
    
    df_zona = df_filtered[df_filtered['restaurant_zone'] == zona_sel] #Filtramos datos SOLO para esa zona
    
    if not df_zona.empty: #Si es que df_zona NO está vacío, se ejecutará el código que sigue
        vehiculos_en_zona = df_zona['delivery_mode'].unique()
        datos_para_box = [] #Se crea una lista con la variable 'datos_para_box'
        labels_box = [] #Se crea una lista con la variable 'labels_box'
        
        for v in vehiculos_en_zona: #Se itera 'v' en 'vehiculos_en_zona'
            tiempos = df_zona[df_zona['delivery_mode'] == v]['delivery_time_min'] #Extraemos los tiempos solo para ese vehículo en esa zona 
            datos_para_box.append(tiempos) #Mandamos los tiempos de ese tipo de vehículo a 'datos_para_box'
            labels_box.append(v) #Mandamos el tipo de vehículo al cual pertenecen estos tiempos
            
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        ax3.boxplot(datos_para_box, labels=labels_box, patch_artist=True) #Creamos la figura de boxplot
        
        ax3.set_title(f"Variabilidad de Tiempos en {zona_sel}")
        ax3.set_ylabel("Tiempo (min)")
        ax3.set_xlabel("Tipo de Vehículo")
        ax3.grid(True, linestyle='--', alpha=0.3)
        
        st.pyplot(fig3)
        st.caption("La línea naranja dentro de la caja indica la mediana de tiempo.") #Escribe un texto (pequeño) bajo el gráfico
        with st.expander("Ver datos detallados de la flota"):
            st.dataframe(df_zona)
    else:
        st.warning(f"No hay envíos en la zona {zona_sel} con los filtros seleccionados.") #Parte del manejo de errores en caso de que no cumpla con los requerimientos.

#Distancia tiempo
with tab3:
    st.subheader("Relación Distancia vs Tiempo") #Encabezado del gráfico (distinto de tittle)
    
    
    selec_dist_tiempo = st.radio( 
        "Colorear puntos por:",
        ["Nivel de Tráfico", "Tipo de Vehículo"],
        horizontal=True
    ) #st.radio botón donde visualizas todas las opciones pero eliges una (diferente a selectbox)
    
    
    col_map = {"Nivel de Tráfico": "traffic_level", "Tipo de Vehículo": "delivery_mode"} #"Traduce" la columna para saber qué parte del código debe tomar el programa y cuál se selecciona
    columna_elegida = col_map[selec_dist_tiempo] 
    
    #Scatter gráfico 4
    if not df_filtered.empty:
        fig4, ax4 = plt.subplots(figsize=(9, 6))
        
        
        grupos = df_filtered.groupby(columna_elegida) #Ocupa la columna elegida con "col_map"

        
        for nombre, grupo in grupos:
            ax4.scatter(grupo['distance_km'], grupo['delivery_time_min'], label=nombre, alpha=0.7) #customizacion scatter (alpha=transparencia)
            
        ax4.set_xlabel("Distancia (km)")
        ax4.set_ylabel("Tiempo de Entrega (min)")
        ax4.legend(title=selec_dist_tiempo) # Muestra la leyenda automática (la leyenda es el recuadro pequeño con nombres)
        ax4.grid(True, alpha=0.3)
        
        st.pyplot(fig4)
    
    st.divider()
    
    col_z1, col_z2 = st.columns(2)
    
    # Pedidos por zona (cliente)
    with col_z1:
        st.subheader("Pedidos por Zona (Cliente)")
        conteo_clientes = df_filtered['customer_zone'].value_counts()# Contamos cuántos pedidos hay por zona (se ordena con el value_counts())

        color_elegido1 = st.color_picker("Elige un color para las barras", "#00f900") #Variable para elegir color a gusto del Usuario

        #Gráfico 5 (barras)
        fig5, ax5 = plt.subplots()
        ax5.bar(conteo_clientes.index, conteo_clientes.values, color=color_elegido1)
        ax5.set_ylabel("Cantidad")
        plt.setp(ax5.get_xticklabels(), rotation=45)
        st.pyplot(fig5) # Rotamos 45 grados las etiquetas para que quepan en su espacio del gráfico
        with st.expander("Ver datos detallados de la flota"):
            st.dataframe(conteo_clientes)
    #Pedidos por zona (restaurante)
    with col_z2:
        st.subheader("Pedidos por Zona (Restaurante)") 
        datos_grafico = df["restaurant_zone"].value_counts() #Lee df y ordena
        
        color_elegido2 = st.color_picker("Elige un color para las barras", "#ffcc99") #Variable para elegir color a gusto del Usuario
        
        #Gráfico 6

        fig6, ax6 = plt.subplots(figsize=(5, 3))
        ax6.bar(datos_grafico.index, datos_grafico.values, color=color_elegido2) #Predetermina el color elegido arriba
        ax6.set_title("Pedidos por Zona")
        ax6.set_ylabel("Cantidad")
        st.pyplot(fig6, use_container_width=False) #A parte de plotear evita que el gráfico se estire según la página
        st.write("Detalle de los datos:", datos_grafico) #Tabla de datos numérica
        with st.expander("Ver datos detallados de la flota"):
            st.dataframe(datos_grafico)
