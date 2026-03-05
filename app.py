import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE BASE DE DATOS ---
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "Logistics2026!")

@st.cache_resource
def get_driver():
    return GraphDatabase.driver(URI, auth=AUTH)

# --- FUNCIONES DE GRAFOS Y RUTAS ---
def calcular_ruta(origen, destino, criterio_peso, peso_camion):
    driver = get_driver()
    graph_name = f"grafo_temporal_{criterio_peso}"
    
    query_drop = f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName"
    
    query_project = f"""
    CALL gds.graph.project.cypher(
        '{graph_name}',
        'MATCH (n) RETURN id(n) AS id',
        'MATCH (n)-[r:CONECTA_A]->(m) WHERE r.limite_peso >= $peso_camion RETURN id(n) AS source, id(m) AS target, r.{criterio_peso} AS weight',
        {{parameters: {{peso_camion: $peso_camion}}}}
    )
    YIELD graphName
    """
    
    query_algo = f"""
    MATCH (o:Almacen {{id: $origen}}), (d:PuntoEntrega {{id: $destino}})
    CALL gds.shortestPath.dijkstra.stream('{graph_name}', {{
        sourceNode: o,
        targetNode: d,
        relationshipWeightProperty: 'weight'
    }})
    YIELD totalCost, nodeIds
    RETURN totalCost, [nodeId IN nodeIds | gds.util.asNode(nodeId).id] AS ruta
    """
    
    with driver.session() as session:
        session.run(query_drop)
        session.run(query_project, peso_camion=peso_camion)
        result = session.run(query_algo, origen=origen, destino=destino)
        
        costo = None
        ruta = None
        for record in result:
            costo = record["totalCost"]
            ruta = record["ruta"]
            
        session.run(query_drop)
        return costo, ruta

def obtener_estadisticas_nodos():
    driver = get_driver()
    query = "MATCH (n) RETURN labels(n)[0] as Etiqueta, count(n) as Total"
    with driver.session() as session:
        result = session.run(query)
        return pd.DataFrame([record.values() for record in result], columns=["Etiqueta", "Total"])

def obtener_estadisticas_rutas():
    driver = get_driver()
    query = """
    MATCH ()-[r:CONECTA_A]->()
    WITH r.limite_peso as limite
    RETURN 
        CASE 
            WHEN limite < 10 THEN 'Carga Ligera (<10t)'
            WHEN limite >= 10 AND limite <= 20 THEN 'Carga Media (10-20t)'
            ELSE 'Carga Pesada (>20t)'
        END as Categoria,
        count(*) as Cantidad
    """
    with driver.session() as session:
        result = session.run(query)
        return pd.DataFrame([record.values() for record in result], columns=["Categoria", "Cantidad"])


# --- INTERFAZ GRÁFICA (STREAMLIT) ---
st.set_page_config(page_title="Logistics Optimizer", page_icon="🚚", layout="wide")

st.title("🚚 Logistics Optimizer (Smart Routing)")
st.markdown("Sistema de gestión de logística con Neo4j y Graph Data Science.")

# Paneles laterales (Asegúrate de que esto esté solo una vez)
st.sidebar.header("📍 Parámetros de Ruta")
origen_id = st.sidebar.text_input("ID del Almacén de Origen", value="A1")
destino_id = st.sidebar.text_input("ID del Cliente Destino", value="P1")

st.sidebar.markdown("---")
st.sidebar.header("⚖️ Restricciones de Carga")
peso_camion = st.sidebar.slider("Peso del Camión (Toneladas)", min_value=1, max_value=30, value=10)

# Botón de cálculo
if st.sidebar.button("Optimizar Ruta", type="primary"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📏 Por Distancia")
        costo_dist, ruta_dist = calcular_ruta(origen_id, destino_id, "distancia", peso_camion)
        if ruta_dist:
            st.metric(label="Distancia Total (km)", value=round(costo_dist, 2))
            st.success(" ➔ ".join(ruta_dist))
        else:
            st.error("Ruta bloqueada.")

    with col2:
        st.subheader("⏱️ Por Tiempo")
        costo_tiempo, ruta_tiempo = calcular_ruta(origen_id, destino_id, "tiempo_estimado", peso_camion)
        if ruta_tiempo:
            st.metric(label="Tiempo Estimado (min)", value=round(costo_tiempo, 2))
            st.info(" ➔ ".join(ruta_tiempo))
        else:
            st.error("Ruta bloqueada.")
            
    with col3:
        st.subheader("💰 Por Costo Operativo")
        costo_op, ruta_op = calcular_ruta(origen_id, destino_id, "costo_operativo", peso_camion)
        if ruta_op:
            st.metric(label="Costo Fórmula (Dist*Traf)", value=round(costo_op, 2))
            st.warning(" ➔ ".join(ruta_op))
        else:
            st.error("Ruta bloqueada.")

    # --- SECCIÓN DE DASHBOARD VISUAL (DINÁMICO) ---
    st.markdown("---")
    st.header("📊 Comparativa de Rendimiento de Rutas")
    
    if ruta_dist or ruta_tiempo or ruta_op:
        val_dist = costo_dist if ruta_dist else 0
        val_tiempo = costo_tiempo if ruta_tiempo else 0
        val_op = costo_op if ruta_op else 0
        
        saltos_dist = len(ruta_dist) if ruta_dist else 0
        saltos_tiempo = len(ruta_tiempo) if ruta_tiempo else 0
        saltos_op = len(ruta_op) if ruta_op else 0

        colA, colB = st.columns(2)
        
        with colA:
            df_valores = pd.DataFrame({
                "Escenario": ["Distancia", "Tiempo", "Costo Operativo"],
                "Valor": [val_dist, val_tiempo, val_op]
            })
            fig_valores = px.bar(df_valores, x="Escenario", y="Valor", color="Escenario",
                                 title="Comparación de Costos Totales (Más bajo es mejor)", text_auto='.2f')
            st.plotly_chart(fig_valores, use_container_width=True)
            
        with colB:
            df_saltos = pd.DataFrame({
                "Escenario": ["Distancia", "Tiempo", "Costo Operativo"],
                "Nodos Recorridos": [saltos_dist, saltos_tiempo, saltos_op]
            })
            fig_saltos = px.bar(df_saltos, x="Escenario", y="Nodos Recorridos", color="Escenario",
                                title="Cantidad de Calles Recorridas (Saltos)", text_auto=True)
            fig_saltos.update_traces(marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'])
            st.plotly_chart(fig_saltos, use_container_width=True)

# --- SECCIÓN DE GRÁFICOS ESTÁTICOS (ESTADO GLOBAL) ---
st.markdown("---")
st.header("🌍 Estado Global de la Ciudad")

colX, colY = st.columns(2)

with colX:
    df_nodos = obtener_estadisticas_nodos()
    if not df_nodos.empty:
        fig_bar_global = px.bar(df_nodos, x="Etiqueta", y="Total", color="Etiqueta", 
                         title="Distribución de Nodos en la Ciudad",
                         text_auto=True)
        st.plotly_chart(fig_bar_global, use_container_width=True)

with colY:
    df_rutas = obtener_estadisticas_rutas()
    if not df_rutas.empty:
        fig_pie_global = px.pie(df_rutas, names="Categoria", values="Cantidad", 
                         title="Capacidad de Vías (Tonelaje)",
                         hole=0.4) 
        st.plotly_chart(fig_pie_global, use_container_width=True)