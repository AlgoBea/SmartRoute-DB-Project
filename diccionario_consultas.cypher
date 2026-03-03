// 1. Proyección del Grafo en Memoria (Requisito GDS)
CALL gds.graph.project(
  'grafoLogistico',
  ['Almacen', 'Interseccion', 'PuntoEntrega'],
  'CONECTA_A',
  { relationshipProperties: ['distancia', 'tiempo_estimado', 'estado_trafico'] }
);

// 2. Algoritmo Dijkstra - Ruta por Distancia
MATCH (origen:Almacen {id: 'A1'}), (destino:PuntoEntrega {id: 'P1'})
CALL gds.shortestPath.dijkstra.stream('grafoLogistico', {
    sourceNode: origen,
    targetNode: destino,
    relationshipWeightProperty: 'distancia'
})
YIELD totalCost, nodeIds
RETURN 'Optimizado por Distancia' AS Criterio, totalCost AS Valor_Total, 
[nodeId IN nodeIds | gds.util.asNode(nodeId).id] AS Ruta_Optima;

// 3. Algoritmo Dijkstra - Ruta por Tiempo/Tráfico
MATCH (origen:Almacen {id: 'A1'}), (destino:PuntoEntrega {id: 'P1'})
CALL gds.shortestPath.dijkstra.stream('grafoLogistico', {
    sourceNode: origen,
    targetNode: destino,
    relationshipWeightProperty: 'tiempo_estimado'
})
YIELD totalCost, nodeIds
RETURN 'Optimizado por Tiempo' AS Criterio, totalCost AS Valor_Total, 
[nodeId IN nodeIds | gds.util.asNode(nodeId).id] AS Ruta_Optima;

// 4. Identificar Cuellos de Botella Logísticos (Intersecciones más críticas)
MATCH (i:Interseccion)-[r:CONECTA_A]->()
WITH i, count(r) AS rutas_salientes, avg(r.estado_trafico) AS trafico_promedio
WHERE rutas_salientes >= 3
RETURN i.id AS Nodo_Interseccion, rutas_salientes, trafico_promedio
ORDER BY trafico_promedio DESC, rutas_salientes DESC
LIMIT 5;

// 5. Desglose de Nodos de la Ruta Óptima paso a paso
MATCH ruta = (o:Almacen {id: 'A1'})-[calles:CONECTA_A*1..10]->(d:PuntoEntrega {id: 'P1'})
WITH nodes(ruta) AS nodos_ruta, reduce(s = 0, c IN calles | s + c.costo_operativo) AS costo_total
ORDER BY costo_total ASC 
LIMIT 1
UNWIND nodos_ruta AS paso_ruta
RETURN paso_ruta.id AS Identificador, labels(paso_ruta)[0] AS Tipo_Lugar;