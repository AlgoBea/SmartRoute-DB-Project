import streamlit as st
from neo4j import GraphDatabase

# Configuración de conexión a tu Docker local
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "Logistics2026!")

# Función para conectarnos a la base de datos
@st.cache_resource
def get_driver():
    return GraphDatabase.driver(URI, auth=AUTH)

# Función corregida para GDS 2.x (Proyección dinámica de grafos)
def calcular_ruta(origen, destino, criterio_peso, peso_camion):
    driver = get_driver()
    # Nombre temporal del grafo en memoria
    graph_name = f"grafo_temporal_{criterio_peso}"
    
    # PASO 1: Asegurarnos de borrar el grafo si quedó en memoria de una consulta anterior
    query_drop = f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName"
    
    # PASO 2: Crear el grafo en RAM filtrando solo las calles que soportan el camión
    query_project = f"""
    CALL gds.graph.project.cypher(
        '{graph_name}',
        'MATCH (n) RETURN id(n) AS id',
        'MATCH (n)-[r:CONECTA_A]->(m) WHERE r.limite_peso >= $peso_camion RETURN id(n) AS source, id(m) AS target, r.{criterio_peso} AS weight',
        {{parameters: {{peso_camion: $peso_camion}}}}
    )
    YIELD graphName
    """
    
    # PASO 3: Ejecutar Dijkstra sobre el grafo temporal que acabamos de crear
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
        # Ejecutamos las consultas en orden
        session.run(query_drop)
        session.run(query_project, peso_camion=peso_camion)
        result = session.run(query_algo, origen=origen, destino=destino)
        
        costo = None
        ruta = None
        for record in result:
            costo = record["totalCost"]
            ruta = record["ruta"]
            
        # PASO 4: Limpiar la memoria borrando el grafo
        session.run(query_drop)
        
        return costo, ruta

# --- INTERFAZ GRÁFICA (STREAMLIT) ---

st.set_page_config(page_title="Logistics Optimizer", page_icon="🚚", layout="wide")

st.title("🚚 Logistics Optimizer (Smart Routing)")
st.markdown("Sistema de gestión de logística con Neo4j y Graph Data Science.")

# Paneles laterales para los controles
st.sidebar.header("📍 Parámetros de Ruta")
origen_id = st.sidebar.text_input("ID del Almacén de Origen", value="A1")
destino_id = st.sidebar.text_input("ID del Cliente Destino", value="P1")

st.sidebar.markdown("---")
st.sidebar.header("⚖️ Restricciones de Carga")
peso_camion = st.sidebar.slider("Peso del Camión (Toneladas)", min_value=1, max_value=30, value=10)

if st.sidebar.button("Optimizar Ruta", type="primary"):
    col1, col2 = st.columns(2)
    
    # Columna 1: Ruta por Distancia
    with col1:
        st.subheader("📏 Ruta más Corta (Dijkstra)")
        costo_dist, ruta_dist = calcular_ruta(origen_id, destino_id, "distancia", peso_camion)
        
        if ruta_dist:
            st.metric(label="Distancia Total (km)", value=round(costo_dist, 2))
            st.success(" ➔ ".join(ruta_dist))
        else:
            st.error("Ruta bloqueada: el camión es muy pesado para estas calles.")

    # Columna 2: Ruta por Tiempo
    with col2:
        st.subheader("⏱️ Ruta más Rápida (A*/Tiempo)")
        costo_tiempo, ruta_tiempo = calcular_ruta(origen_id, destino_id, "tiempo_estimado", peso_camion)
        
        if ruta_tiempo:
            st.metric(label="Tiempo Estimado (min)", value=round(costo_tiempo, 2))
            st.info(" ➔ ".join(ruta_tiempo))
        else:
            st.error("Ruta bloqueada: el camión es muy pesado para estas calles.")