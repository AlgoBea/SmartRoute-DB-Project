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