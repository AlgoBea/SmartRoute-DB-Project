import random

# Configuración
num_almacenes = random.randint(3, 4)
num_intersecciones = 50
num_puntos = 20
num_relaciones = 200  # cantidad de relaciones a generar

# Generar identificadores
almacenes = [f"A{i+1}" for i in range(num_almacenes)]
intersecciones = [f"I{i+1}" for i in range(num_intersecciones)]
puntos = [f"P{i+1}" for i in range(num_puntos)]

todos_nodos = (
    [("Almacen", id) for id in almacenes]
    + [("Interseccion", id) for id in intersecciones]
    + [("PuntoEntrega", id) for id in puntos]
)

# Función para crear una relación aleatoria entre dos nodos diferentes

def generar_relacion():
    tipo1, id1 = random.choice(todos_nodos)
    tipo2, id2 = random.choice(todos_nodos)
    # evitar autorelaciones
    while tipo1 == tipo2 and id1 == id2:
        tipo2, id2 = random.choice(todos_nodos)

    distancia = round(random.uniform(1.0, 20.0), 1)
    tiempo_estimado = random.randint(5, 45)
    estado_trafico = round(random.uniform(0.01, 0.99), 2)

    return (
        f"CREATE (n1:{tipo1} {{id: '{id1}'}})-[r:CONECTA_A "
        f"{{distancia: {distancia}, tiempo_estimado: {tiempo_estimado}, "
        f"estado_trafico: {estado_trafico}}}]->(n2:{tipo2} {{id: '{id2}'}})"
    )

# Escritura del archivo cypher

with open("carga_masiva.cypher", "w", encoding="utf-8") as f:
    for tipo, nid in todos_nodos:
        # crear nodo
        if tipo == "Almacen":
            line = f"CREATE (a:{tipo} {{id: '{nid}', nombre: 'Almacen {nid[1:]}'}})"
        elif tipo == "Interseccion":
            line = f"CREATE (i:{tipo} {{id: '{nid}', nombre: 'Cruce {nid[1:]}'}})"
        else:
            line = f"CREATE (p:{tipo} {{id: '{nid}'}})"
        f.write(line + "\n")

    # relaciones
    for _ in range(num_relaciones):
        f.write(generar_relacion() + "\n")

print(f"Archivo 'carga_masiva.cypher' generado con {len(todos_nodos)} nodos y {num_relaciones} relaciones.")
