# Logistics Optimizer (Smart Routing)

Sistema de gestión logística diseñado para optimizar rutas de entrega considerando variables dinámicas como tráfico, costo operativo y capacidad de carga. El proyecto utiliza **Neo4j** como motor de base de datos de grafos y la librería **Graph Data Science (GDS)** para el cálculo de rutas óptimas.

## Características Técnicas

* 
**Algoritmos de Grafos (GDS)**: Comparación en tiempo real de **Dijkstra** (optimización por distancia) frente a **A*** (heurística basada en tiempo y tráfico).


* 
**Costo de Ruta**: Implementación de una función de costo dinámica: $Costo = \sum (distancia_i \times factor\_trafico_i)$.


* **Restricciones de Carga**: Filtrado de aristas en tiempo real. Si el peso del camión supera el límite de la vía (`limite_peso`), la ruta es deshabilitada para la consulta.


* 
**Proyecciones en Memoria**: Uso de `gds.graph.project` para crear subgrafos virtuales que optimizan el rendimiento de los algoritmos.



## Stack Tecnológico

* 
**Base de Datos**: Neo4j 5.x + GDS Library + APOC.


* 
**Frontend**: Streamlit (Python).


* **Infraestructura**: Docker & Docker Compose.

## Estructura del Proyecto

* 
`app.py`: Interfaz de usuario y lógica de conexión con Neo4j.


* 
`carga_corregida.cypher`: Script para la creación de nodos (Almacén, Punto Entrega, Intersección) y relaciones (CONECTA_A).


* 
`diccionario_consultas.cypher`: Consultas complejas utilizando WITH, UNWIND y GDS.


* `docker-compose.yml`: Configuración del entorno de contenedores.

## Instalación y Uso

1. **Levantar el entorno**:
```bash
docker-compose up -d

```

2. **Cargar datos**:
Copiar y ejecutar el contenido de `carga_corregida.cypher` en Neo4j Browser.

3. **Instalar dependencias**:
```bash
pip install streamlit neo4j pandas plotly

```

4. **Ejecutar Dashboard**:
```bash
streamlit run app.py

```


## Justificación Técnica: Neo4j vs SQL

Para este caso de optimización logística, Neo4j es superior a las bases de datos relacionales por las siguientes razones:

1. **Eficiencia en Recorridos**: En SQL, encontrar rutas requiere múltiples *JOINs* costosos. En Neo4j, el recorrido de relaciones es una operación de tiempo constante independiente del tamaño total de los datos.

2. 
**Modelo de Datos Natural**: La red vial se representa directamente como un grafo, eliminando la necesidad de tablas intermedias de normalización.

3. 
**Algoritmos Nativos**: Neo4j permite ejecutar algoritmos complejos como Dijkstra o A* directamente sobre la estructura de datos sin necesidad de extraer la información a una aplicación externa.
