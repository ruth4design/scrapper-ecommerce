import pandas as pd
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import json

# Paso 1: Cargar y combinar los datos de múltiples archivos CSV
def cargar_productos(path):
    files = glob.glob(path)
    dfs = []
    for file in files:
        df = pd.read_csv(file)  # Carga todas las columnas
        dfs.append(df)
    productos_df = pd.concat(dfs, ignore_index=True)
    return productos_df

# Paso 2: Preprocesamiento y Vectorización TF-IDF
def vectorizar_productos(productos_df):
    vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
    tfidf_matrix = vectorizer.fit_transform(productos_df['Descripción'])
    return vectorizer, tfidf_matrix

# Paso 3: Función de Búsqueda que devuelve JSON
def buscar_producto(query, productos_df, vectorizer, tfidf_matrix, top_n=10):
    query_tfidf = vectorizer.transform([query])
    cos_similarities = cosine_similarity(query_tfidf, tfidf_matrix).flatten()
    matched_indices = cos_similarities.argsort()[::-1][:top_n]  # Indices de los top_n productos más similares
    
    # Crear lista de diccionarios con los productos encontrados
    productos_encontrados = productos_df.iloc[matched_indices].to_dict(orient='records')
    
    # Convertir a JSON
    productos_json = json.dumps(productos_encontrados, ensure_ascii=False)
    return productos_json

# Ajusta el path según tu estructura de carpetas y archivos
path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../output/plazavea/plaza-vea-2024-02-23_19-44-51.csv'))
productos_df = cargar_productos(path)

vectorizer, tfidf_matrix = vectorizar_productos(productos_df)

# Ejemplo de búsqueda
query = "AUDÍFONOS BLUETOOTH HUAWEI FREEBUDS SE 2 BLANCO"
N = 3
productos_json = buscar_producto(query, productos_df, vectorizer, tfidf_matrix, N)

# Mostrar el JSON de los productos encontrados
# print(productos_json)
formatted_json = json.loads(productos_json)
print(json.dumps(formatted_json, indent=4, ensure_ascii=False))


# from difflib import get_close_matches
# import pandas as pd
# import os
# def generar_n_gramas(texto, n=2):
#     """
#     Genera n-gramas a partir de un texto dado.
    
#     :param texto: El texto de entrada.
#     :param n: El tamaño de los n-gramas.
#     :return: Una lista de n-gramas.
#     """
#     palabras = texto.split()
#     n_gramas = [' '.join(palabras[i:i+n]) for i in range(len(palabras)-n+1)]
#     return n_gramas

# def buscar_por_secuencia(query, lista_productos, n=2):
#     """
#     Busca productos basándose en la coincidencia de n-gramas entre la consulta y los nombres de productos.
    
#     :param query: La consulta de búsqueda.
#     :param lista_productos: Una lista con los nombres de todos los productos.
#     :param n: El tamaño de los n-gramas a considerar.
#     :return: Un diccionario con los productos y su conteo de coincidencias de n-gramas.
#     """
#     query_n_gramas = generar_n_gramas(query, n)
#     coincidencias = {}
    
#     for producto in lista_productos:
#         producto_n_gramas = generar_n_gramas(producto, n)
#         conteo_coincidencias = sum(1 for n_grama in query_n_gramas if n_grama in producto_n_gramas)
        
#         if conteo_coincidencias > 0:
#             coincidencias[producto] = conteo_coincidencias
    
#     # Ordenar productos por conteo de coincidencias
#     coincidencias_ordenadas = dict(sorted(coincidencias.items(), key=lambda item: item[1], reverse=True))
    
#     return coincidencias_ordenadas



# # Cargar el CSV


# abs_path_from_relative = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../output/plazavea/plaza-vea-2024-02-23_19-44-51.csv'))
# df = pd.read_csv(abs_path_from_relative)
# # Lista de nombres de productos del CSV
# lista_nombres_productos = df['Descripción'].tolist()

# # Ejemplo de búsqueda
# nombre_a_buscar = 'Audífonos Bluetooth HUAWEI FREEBUDS SE 2 BLANCO'
# coincidencias = buscar_por_secuencia(nombre_a_buscar, lista_nombres_productos)

# print("Coincidencias encontradas:", coincidencias)
