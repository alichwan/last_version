# TODO:
# - tomar el grafo y hacer un vector que represente todos los predicados (detectores) disponibles
# - dada un conjunto de traces positivas P y negativas N, EN FORMATO LISTA DE CONJUNTOS DE PREDICADOS, construir un arbol
#   - se parte por un nodo raíz 
#   - por cada trace, se toma cada una de las combinaciones de predicados, si existe esa combinación, se sitúa en el siguiente nodo 
#   - si no existe la combinacion, se agrega un nuevo camino, se situa en el siguiente nodo
#   - al llegar a cada hoja su valor toma si es positivo o negativo
# 