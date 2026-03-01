import re

print("Analizando y corrigiendo el archivo de Luismer...")

with open('carga_masiva.cypher', 'r') as f_in, open('carga_corregida.cypher', 'w') as f_out:
    for linea in f_in:
        linea = linea.strip()
        if not linea:
            continue
            
        # Si la línea es una relación (Ruta)
        if 'CONECTA_A' in linea:
            # Magia de Regex para cambiar CREATE por MATCH y estructurarlo bien
            regex = r"CREATE \((n1:[a-zA-Z]+ \{id: '[^']+'\})\)-\[(r:CONECTA_A \{.*?\})\]->\((n2:[a-zA-Z]+ \{id: '[^']+'\})\)"
            reemplazo = r"MATCH (\1), (\3) CREATE (n1)-[\2]->(n2);"
            linea_arreglada = re.sub(regex, reemplazo, linea)
            
            # Si por alguna razón el Regex no hace match, solo le pone el punto y coma
            if linea_arreglada == linea:
                linea_arreglada = linea + ';'
                
            f_out.write(linea_arreglada + "\n")
            
        # Si la línea es crear un nodo (Almacen, Interseccion, etc)
        else:
            if not linea.endswith(';'):
                linea += ';'
            f_out.write(linea + "\n")

print("¡Listo! Tu código perfecto está en 'carga_corregida.cypher'")