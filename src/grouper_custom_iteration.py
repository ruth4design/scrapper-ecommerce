import pandas as pd



# Auxiliary functions
def calcular_similitud(set1, set2):
    interseccion = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return interseccion / union if union > 0 else 0

def determinar_umbral(longitud):
    if longitud <= 3:
        return 0.8
    elif longitud <= 6:
        return 0.7
    elif longitud <= 7:
        return 0.65
    else:
        return 0.45

def main(dataframe: pd.DataFrame):
    # df = pd.read_csv('./Muestra2.csv', encoding='utf-8')
    df = dataframe
    df['product_set'] = df['Descripción'].apply(lambda desc: set(desc.split()))
    df['umbral'] = df['product_set'].apply(lambda desc: determinar_umbral(len(desc)))
    df.sort_values(by=['Descripción'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Inicialización de la columna de grouped_code
    df['grouped_code'] = -1  # Inicializar todos los productos sin grupo

    grouped_code = "00000000"
    for i in range(len(df)):
        # Si el producto ya tiene un grupo, continuar
        if df.at[i, 'grouped_code'] != -1:
            continue
        df.at[i, 'grouped_code'] = grouped_code 
        grupo_base_set = df.at[i, 'product_set']
        umbral_base = df.at[i, 'umbral']

        # Comparar con los 100 productos siguientes
        for j in range(i + 1, min(i + 101, len(df))):
            if df.at[j, 'grouped_code'] != -1:
                continue  # El producto ya está en un grupo

            similitud = calcular_similitud(grupo_base_set, df.at[j, 'product_set'])
            if similitud >= max(umbral_base, df.at[j, 'umbral']):
                df.at[j, 'grouped_code'] = grouped_code
                print(f'{grouped_code} con el producto "{df.at[j, "Descripción"]}".')

        # Generar un nuevo grouped_code
        grouped_code = str(int(grouped_code) + 1).zfill(8)

    # Guardar los resultados
    df.drop(['product_set', 'umbral'], axis=1, inplace=True)

    # convert grouped code to string of 8 characters
    df['grouped_code'] = df['grouped_code'].apply(lambda x: str(x).zfill(8))
    df.rename(columns={'grouped_code': 'Código agrupado'}, inplace=True)
    # df.to_csv('productos_agrupados_optimized.csv', index=False)
    return df
# main()



# import pandas as pd
# from itertools import combinations
# from collections import defaultdict

# # Load data
# df = pd.read_csv('./Muestra2.csv', encoding='utf-8')

# # Auxiliary functions
# def calcular_similitud(set1, set2):
#     interseccion = len(set1.intersection(set2))
#     union = len(set1.union(set2))
#     return interseccion / union if union > 0 else 0

# def determinar_umbral(longitud):
#     if longitud <= 3:
#         return 0.8
#     elif longitud <= 6:
#         return 0.7
#     elif longitud <= 7:
#         return 0.65
#     else:
#         return 0.45

# # Preprocessing: Split 'Nombre' into words and calculate threshold by description
# def main():
#     df['product_set'] = df['Nombre'].apply(lambda desc: set(desc.split()))
#     df['umbral'] = df['product_set'].apply(lambda desc: determinar_umbral(len(desc)))

#     # Grouping
#     grupos = {}
#     grouped_code = 0
#     for i, j in combinations(df.index, 2):
#         similitud = calcular_similitud(df.at[i, 'product_set'], df.at[j, 'product_set'])
#         umbral_i = df.at[i, 'umbral']
#         umbral_j = df.at[j, 'umbral']
        

#         if similitud >= max(umbral_i, umbral_j):
#             encontrado = False
#             for key, value in grupos.items():
#                 if i in value or j in value:
#                     grupos[key].update([i, j])
#                     encontrado = True
#                     break
#             if not encontrado:
#                 grupos[grouped_code] = set([i, j])
#                 print(f"Grupo {grouped_code}: {df.at[i, 'Nombre']} - {df.at[j, 'Nombre']}")
#                 grouped_code += 1

#     # Assign products without a group to their own group
#     todos_los_indices = set(df.index)
#     indices_en_grupos = set(k for v in grupos.values() for k in v)
#     indices_sin_grupo = todos_los_indices - indices_en_grupos

#     for indice in indices_sin_grupo:
#         grupos[grouped_code] = set([indice])
#         grouped_code += 1

#     # Create DataFrame with groups
#     grupos_df = pd.DataFrame()
#     for key, value in grupos.items():
#         for v in value:
#             row = df.loc[v].copy()
#             row['grouped_code'] = key
#             grupos_df = grupos_df._append(row, ignore_index=True)

#     # Drop auxiliary columns
#     grupos_df.drop(['product_set', 'umbral'], axis=1, inplace=True)

#     # Save to CSV
#     grupos_df.to_csv('productos_agrupados_slow.csv', index=False)
#     print("Productos agrupados guardados en 'productos_agrupados.csv'.")
