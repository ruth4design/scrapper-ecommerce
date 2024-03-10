import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import re
import nltk

# Asegurar que las stopwords estén disponibles
nltk.download('stopwords')

# Función para preprocesar los nombres
def preprocesar_nombre(nombre):
    nombre = re.sub(r'[^\w\s]', '', nombre).lower()  # Eliminar caracteres especiales y convertir a minúsculas
    # eliminar numeros 
    nombre = re.sub(r'\d+', '', nombre)
    palabras = nombre.split()

    # Eliminar stopwords en español
    stop_words = set(nltk.corpus.stopwords.words('spanish'))
    palabras = [palabra for palabra in palabras if palabra not in stop_words]

    # Asignar pesos decrecientes a las palabras según su posición en el nombre
    palabras_pesadas = []
    peso_inicial = 2.0  # Peso inicial para la primera palabra
    for i, palabra in enumerate(palabras):
        peso = peso_inicial / (i + 1)  # Asignar peso decreciente
        palabras_pesadas.append((palabra, peso))

    rest_of_words = [palabra for palabra in palabras if palabra not in [x[0] for x in palabras_pesadas]]
    # Construir el nombre preprocesado con los pesos asignados
    nombre_preprocesado = ' '.join([palabra * int(peso) for palabra, peso in palabras_pesadas]) + ' ' + ' '.join(rest_of_words)
    return nombre_preprocesado



def main():

    # Cargar los datos
    df = pd.read_csv('./Muestra2.csv')

    # Preprocesar los nombres
    df['nombre_normalizado'] = df['Nombre'].apply(preprocesar_nombre)
    # df.sort_values(by=['nombre_normalizado'], inplace=True)
    # Vectorización TF-IDF
    vectorizer = TfidfVectorizer(max_df=0.5, min_df=2, ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(df['nombre_normalizado'])

    # No necesitamos escalar los datos TF-IDF para DBSCAN ya que no se basa en la magnitud de los vectores
    # Encontrar el valor óptimo de eps podría ser desafiante automáticamente; considera una aproximación basada en pruebas
    eps_optimo = 0.27  # Este valor puede necesitar ajuste

    # Aplicar DBSCAN
    dbscan = DBSCAN(eps=eps_optimo, min_samples=1, metric='cosine')  # Usando 'cosine' porque es más intuitivo para texto
    clusters = dbscan.fit_predict(tfidf_matrix)

    # Asignar los IDs de clusters a los datos originales
    df['cluster_id'] = clusters

    # Opcional: Inspeccionar los resultados
    # print(df[['Nombre', 'cluster_id']].head(30))

    #  remove the nombre_normalizado column
    df = df.drop(columns=['nombre_normalizado'])
    # Guardar a un nuevo CSV si es necesario
    df.to_csv('./productos_agrupados_intermediate.csv', index=False)

if __name__ == "__main__":
    main()
