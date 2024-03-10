from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse, Response
from io import StringIO

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.cluster import KMeans
from src.grouper_custom_iteration import main as grouper
import json

app = FastAPI()

# Estructura para almacenar los datos en memoria
datos_vectorizados = {"vectorizer": None, "tfidf_matrix": None, "productos_df": None}

# def cluster_productos(tfidf_matrix, n_clusters=5):
#     kmeans = KMeans(n_clusters=n_clusters, random_state=42)
#     # Perform clustering
#     kmeans.fit(tfidf_matrix)
#     # Return the cluster labels
#     return kmeans.labels_

def cargar_productos(dfs):
    productos_df = pd.concat(dfs, ignore_index=True)
    return productos_df

def vectorizar_productos(productos_df):
    vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
    tfidf_matrix = vectorizer.fit_transform(productos_df['Descripción'])
    return vectorizer, tfidf_matrix

def buscar_producto(query, vectorizer, tfidf_matrix, productos_df, top_n=10):
    query_tfidf = vectorizer.transform([query])
    cos_similarities = cosine_similarity(query_tfidf, tfidf_matrix).flatten()
    matched_indices = cos_similarities.argsort()[::-1][:top_n]
    
    productos_encontrados = productos_df.iloc[matched_indices]
    productos_json = productos_encontrados.to_json(orient='records', force_ascii=False)
    return productos_json

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    global datos_vectorizados
    dfs = []
    for file in files:
        df = pd.read_csv(file.file, encoding="utf-8")
        dfs.append(df)
    
    productos_df = cargar_productos(dfs)

    productos_df = productos_df.dropna(subset=["Descripción"])

    # trim column Descripción
    productos_df['Descripción'] = productos_df['Descripción'].str.strip()
    productos_df.sort_values(by=['Descripción'], inplace=True)
    vectorizer, tfidf_matrix = vectorizar_productos(productos_df)
    
    
    datos_vectorizados["vectorizer"] = vectorizer
    datos_vectorizados["tfidf_matrix"] = tfidf_matrix
    datos_vectorizados["productos_df"] = productos_df
    
    return {"detail": f"{len(files)} files uploaded and processed successfully"}


@app.get("/search")
async def search(query: str):
    global datos_vectorizados
    if datos_vectorizados["vectorizer"] is None:
        raise HTTPException(status_code=404, detail="No data available. Please upload files first.")
    
    productos_json = buscar_producto(query, **datos_vectorizados)
    
    return JSONResponse(content=json.loads(productos_json))

@app.get("/download/{query}")
async def download(query: str):
    global datos_vectorizados
    if datos_vectorizados["vectorizer"] is None:
        raise HTTPException(status_code=404, detail="No data available. Please upload files first.")
    length_data_vectorized = len(datos_vectorizados["productos_df"])
    productos_json = buscar_producto(query, **datos_vectorizados, top_n=length_data_vectorized)
    productos_df = pd.read_json(productos_json)
    csv = productos_df.to_csv(index=False)
    return Response(content=csv, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={query}.csv"})


@app.get("/download_clustered")
async def download_clustered():
    global datos_vectorizados
    if datos_vectorizados["vectorizer"] is None or "productos_df" not in datos_vectorizados:
        raise HTTPException(status_code=404, detail="No data available. Please upload files first.")
    
    # Use the DataFrame with ClusterID included
    productos_df = datos_vectorizados["productos_df"]
    
    # Grouping products by ClusterID
    grouped_df = productos_df.sort_values(by='ClusterID')
    
    # Convert the grouped DataFrame to CSV
    output = StringIO()
    grouped_df.to_csv(output, index=False)
    output.seek(0)
    
    # Return the CSV response
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=clustered_products.csv"})


@app.get("/group")
async def group_products():
    global datos_vectorizados
    if datos_vectorizados["vectorizer"] is None or "productos_df" not in datos_vectorizados:
        raise HTTPException(status_code=404, detail="No data available. Please upload files first.")
    
    # Use the grouper function to get 'Código agrupado'
    grouped_products = grouper(datos_vectorizados["productos_df"])

    # Step 1: Determine the uniqueness of 'Competidor' within each 'Código agrupado'
    unique_competitor_by_group = grouped_products.groupby('Código agrupado')['Competidor'].nunique()

    # Identify groups with more than one unique 'Competidor' value
    groups_with_multiple_competitors = unique_competitor_by_group[unique_competitor_by_group > 1].index

    # Filter the grouped_products to exclude groups with only one unique 'Competidor'
    filtered_products = grouped_products[grouped_products['Código agrupado'].isin(groups_with_multiple_competitors)]

    # Assuming the rest of your logic is meant to process filtered_products
    counter_products_grouped = filtered_products["Código agrupado"].value_counts().rename('Cantidad de productos')
    filtered_products = filtered_products.merge(counter_products_grouped.to_frame(), left_on='Código agrupado', right_index=True)
    filtered_products_sorted = filtered_products.sort_values(by=['Cantidad de productos', 'Código agrupado', 'Código Web Individual'], ascending=[False, True, True])

    new_headers = ['Código agrupado','Categoría', 'Subcategoría', 'Sección', 'Descripción', 'Código Web Individual', 'Marca', 'Tiene Stock', 'Precio Regular', 'Precio Promo', 'Precio Tarjeta', 'Página Web', 'Competidor']

    filtered_products_sorted = filtered_products_sorted[new_headers]

    # rename Código Web Individual to SKU
    filtered_products_sorted.rename(columns={'Código Web Individual': 'SKU', "Competidor":"Site"}, inplace=True)
    # Drop the 'Cantidad de productos' column as it's no longer needed in the output
    # filtered_products_sorted = filtered_products_sorted.drop(columns=['Cantidad de productos'])

    # Generate CSV from the filtered and sorted DataFrame
    csv = filtered_products_sorted.to_csv(index=False)
    return Response(content=csv, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=filtered_grouped_products.csv"})
