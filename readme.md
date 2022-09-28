# Fórmulas from traces

En el contexto de navegación de espacios físicos por agentes móviles a partir de instrucciónes en lenguaje natural, se han hecho varios trabajos para hayar una manera conveniente de llevarlo a cabo.

Algúnos de estos enfoques requieren encontrar si una fórmula en lógica temporal lineal (LTL) es satisfacible dadas unas "_traces_" (secuencia de conjuntos de predicados) [Riener, 2018].

Se propone resolver la satisfacibilidad de fórmulas usando el solver de Clingo (Answer Set Programming), en lugar de un solver de optimización. Una distinción es que este enfoque permite, de hecho, generar traces satisfacibles.

Qué encontrarás en este repositorio:

- `dags.py`: este código tiene las funciones necesarias para crear gráfos acíclicos dirigidos con cierta cantidad de nodos y ordenados de manera determinista.
- `traces_ch/`:
  - Esta carpeta con 2 archivos en formato JSON que contienen una habitación, uno de los archivos muestra las conecciones del agente; y el otro muestra los objetos que son detectados en cada uno de los nodos del gráfo de navegación.
  - `trace_generator.py`: Este módulo toma el gráfo y construye traces aleatorias en formato conveniente para ser procesado por el código escrito en Clingo.
- `main.lp`: código escrito en ASP, al compilarse entrega si el programa es satisfacible o no, de serlo, entrega una fórmula en LTL con sus respectivos operadores y predicados que satisfacen las traces.
- `main.py`: programa que se encarga de coordinar el experimento; se genera un trace con s pasos, se prueban fórmulas correspondiantes a DAGS con n nodos o con distintas estructuras, si la fórmula no es satisfacible se van aumentando nodos del DAG hasta que se satisfaga o alcance el máximo de nodos permitidos (en tal caso se concluye que es insatisfacible). Se obtienen los tiempos que tarda en encontrar una respuestaa la trace.

Referencias:

- H. Riener, "Exact Synthesis of LTL Properties from Traces," 2019 Forum for Specification and Design Languages (FDL), 2019, pp. 1-6, doi: 10.1109/FDL.2019.8876900.
