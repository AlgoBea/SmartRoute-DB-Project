# Logistics Optimizer (Smart Routing)

Sistema de optimización de rutas logísticas basado en grafos nativos, diseñado para calcular trayectorias eficientes considerando variables dinámicas como tráfico, distancia y restricciones de carga pesada.

## Estructura del Proyecto

* **/docs**: Informe técnico, justificación teórica y diccionario de consultas Cypher.
* **/scripts_carga**: Scripts `.cypher` para la creación del grafo y enriquecimiento de datos.
* **/app**: Código fuente de la interfaz de visualización y lógica de integración.

## Requisitos Previos

* **Neo4j Database**: Versión 5.x o superior.
* **GDS Library**: Graph Data Science plugin instalado en la instancia de Neo4j.
* **APOC Library**: (Opcional) para funciones extendidas de carga de datos.

## Instalación y Configuración

1. **Carga de Datos**: Ejecución del contenido de `scripts_carga/carga_corregida.cypher` en su consola de Neo4j para crear los 3 nodos principales (`Almacen`, `Interseccion`, `PuntoEntrega`) y sus relaciones.
2. **Enriquecimiento de Atributos**: Para habilitar el filtrado por restricciones de carga (Requerimiento Técnico 3), ejecute el siguiente parche para asignar capacidades de carga aleatorias a las rutas:
```cypher
MATCH ()-[r:CONECTA_A]->()
SET r.capacidad_toneladas = range(10, 40)[toInteger(rand() * 30)];

```


3. **Proyección del Grafo**: Antes de ejecutar algoritmos de GDS, proyección del grafo en memoria:
```cypher
CALL gds.graph.project(
  'grafoLogistico',
  ['Almacen', 'Interseccion', 'PuntoEntrega'],
  'CONECTA_A',
  { relationshipProperties: ['distancia', 'tiempo_estimado', 'estado_trafico'] }
);

```



## Funcionalidades Implementadas

* **Algoritmos de Graph Data Science**: Comparativa de rendimiento y precisión entre Dijkstra (basado en distancia física) y A* (basado en tiempo y tráfico).
* **Cálculo Dinámico de Costos**: Función de costo personalizada que integra la distancia con el factor de tráfico en tiempo real: `Costo = Σ(distancia * estado_trafico)`.
* **Filtrado de Aristas**: Capacidad de excluir rutas en la consulta de búsqueda si el vehículo supera la `capacidad_toneladas` permitida por la vía.
* **Visualización**: Interfaz conectada a la base de datos para mostrar los resultados de las rutas óptimas.

## Justificación Tecnológica

Este proyecto utiliza **Neo4j** aprovechando la **Adyacencia sin Índices**. A diferencia de los sistemas SQL, el recorrido de rutas en este optimizador no depende de JOINs costosos, permitiendo una complejidad computacional de O(1) por salto, lo que garantiza escalabilidad ante redes viales de gran tamaño.