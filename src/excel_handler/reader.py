# src/excel_handler/reader.py

import pandas as pd

# Mantenemos leer_excel_muestra por si la necesitas para inspecciones rápidas en el futuro
def leer_excel_muestra(ruta_archivo: str, nombre_hoja: str, fila_encabezados_idx: int, num_filas_datos: int):
    """
    Lee una muestra de un archivo Excel, extrayendo encabezados y un número específico de filas de datos.
    """
    print(f"--- Iniciando lectura de MUESTRA del archivo: {ruta_archivo} ---")
    try:
        df = pd.read_excel(
            ruta_archivo,
            sheet_name=nombre_hoja,
            header=fila_encabezados_idx,
            nrows=num_filas_datos,
            engine='openpyxl'
        )
        encabezados = df.columns.tolist()
        print("\n--- Encabezados Detectados (Muestra) ---")
        if not encabezados:
            print("No se detectaron encabezados. Verifica la configuración de 'fila_encabezados_idx'.")
        else:
            for i, encabezado in enumerate(encabezados):
                print(f"  {i+1}. {encabezado}")

        datos_pacientes = df.to_dict(orient='records')
        print(f"\n--- {len(datos_pacientes)} Primera(s) Fila(s) de Datos Leídas (Muestra) ---")
        if not datos_pacientes:
            print("No se encontraron datos de pacientes con los parámetros dados (o nrows=0).")
        else:
            for i, paciente_data in enumerate(datos_pacientes):
                fila_excel_real = fila_encabezados_idx + 1 + i + 1
                print(f"\nDatos Fila de Paciente {i+1} (Corresponde a Excel Fila ~{fila_excel_real}):")
                for key, value in paciente_data.items():
                    print(f"  {key}: {value} (Tipo: {type(value).__name__})")
        
        print("\n--- Lectura de muestra finalizada exitosamente. ---")
        return encabezados, datos_pacientes

    except FileNotFoundError:
        print(f"Error: El archivo '{ruta_archivo}' no fue encontrado.")
        return None, None
    except ValueError as ve:
        if f"Worksheet named '{nombre_hoja}' not found" in str(ve) or \
           f"'{nombre_hoja}'" in str(ve):
             print(f"Error: La hoja '{nombre_hoja}' no fue encontrada en el archivo '{ruta_archivo}'.")
        else:
            print(f"Error de valor al procesar el Excel: {ve}")
        return None, None
    except Exception as e:
        print(f"Error inesperado al leer la muestra del archivo Excel: {e}")
        return None, None

def obtener_datos_filtrados_excel(ruta_archivo: str, nombre_hoja: str, fila_encabezados_idx: int, criterios_filtro: dict):
    """
    Lee un archivo Excel completo, aplica filtros y devuelve el DataFrame filtrado.
    Incluye logs de depuración para el conteo de filas después de cada filtro.
    """
    print(f"\n--- Iniciando lectura y filtrado del archivo: {ruta_archivo}, Hoja: {nombre_hoja} ---")
    try:
        df = pd.read_excel(
            ruta_archivo,
            sheet_name=nombre_hoja,
            header=fila_encabezados_idx,
            engine='openpyxl'
        )

        if df.empty:
            print("El DataFrame está vacío después de la lectura inicial (antes de filtrar).")
            return None

        print(f"Filas leídas antes de cualquier filtro específico: {len(df)}")

        # (Opcional) Imprimir tipos de las columnas de filtro para depuración
        print("\n--- Tipos de datos de columnas de filtro (antes de filtrar) ---")
        for col_filtro in criterios_filtro.keys():
            if col_filtro in df.columns:
                print(f"Columna '{col_filtro}': {df[col_filtro].dtype}")
                # Imprimir algunos valores únicos para ver qué hay
                # print(f"  Valores únicos (muestra) para '{col_filtro}': {df[col_filtro].astype(str).str.strip().str.upper().unique()[:5]}")
            else:
                print(f"Columna '{col_filtro}': No encontrada en el DataFrame.")
        print("------------------------------------------------------------")


        mascara_final = pd.Series([True] * len(df), index=df.index)
        print(f"\nConteo inicial de filas candidatas (antes de filtros detallados): {mascara_final.sum()}")

        for columna, valor_criterio in criterios_filtro.items():
            if columna not in df.columns:
                print(f"ADVERTENCIA: La columna de filtro '{columna}' no existe en el Excel. Se omitirá este filtro.")
                continue

            mascara_columna_actual = pd.Series([False] * len(df), index=df.index) # Máscara para esta columna específica

            # Es importante trabajar con una copia o directamente sobre la columna del df para la comparación
            # Evitar modificar df[columna] directamente si no es la intención final
            columna_para_comparar = df[columna]

            if columna in ["USUARIO:", "ES PYP:", "ESPECIALIDAD:"]:
                # Normalizar columna del DataFrame a string, mayúsculas y sin espacios
                columna_norm_df = columna_para_comparar.astype(str).str.upper().str.strip()
                
                if isinstance(valor_criterio, list): # Para "USUARIO:" que es una lista
                    # Normalizar cada valor en la lista de criterios
                    valores_criterio_norm = [str(v).upper().strip() for v in valor_criterio]
                    mascara_columna_actual = columna_norm_df.isin(valores_criterio_norm)
                    # print(f"  DEBUG: {columna} (lista) - DF vals: {columna_norm_df.unique()[:10]}, Criterio: {valores_criterio_norm}")
                else: # Para "ES PYP:", "ESPECIALIDAD:"
                    # Normalizar el valor del criterio
                    valor_criterio_norm = str(valor_criterio).upper().strip()
                    mascara_columna_actual = (columna_norm_df == valor_criterio_norm)
                    # print(f"  DEBUG: {columna} - DF vals: {columna_norm_df.unique()[:10]}, Criterio: '{valor_criterio_norm}'")
            
            elif columna == "CUPS:":
                # Estrategia: convertir a string para robustez, y quitar decimales si los hubiera como .0
                columna_norm_df_cups = columna_para_comparar.astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                valor_criterio_cups_str = str(valor_criterio).strip() # valor_criterio es 890201
                mascara_columna_actual = (columna_norm_df_cups == valor_criterio_cups_str)
                # print(f"  DEBUG: {columna} - DF vals (str): {columna_norm_df_cups.unique()[:10]}, Criterio (str): '{valor_criterio_cups_str}'")
            
            else: # Para cualquier otra columna no especificada, hacer una comparación directa (podría necesitar ajustes)
                print(f"INFO: Aplicando filtro genérico para columna '{columna}'.")
                mascara_columna_actual = (columna_para_comparar == valor_criterio)


            # Aplicar la máscara de esta columna a la máscara final acumulada
            mascara_final &= mascara_columna_actual
            print(f"Filas después de aplicar filtro para '{columna}' (criterio: {valor_criterio}): {mascara_final.sum()}")

        df_filtrado = df[mascara_final].copy() # Usar .copy() para evitar SettingWithCopyWarning más adelante si se modifica
        
        # No es necesario imprimir aquí len(df_filtrado) ya que mascara_final.sum() da el mismo resultado
        # print(f"Filas después de aplicar todos los filtros: {len(df_filtrado)}")

        return df_filtrado

    except FileNotFoundError:
        print(f"Error: El archivo '{ruta_archivo}' no fue encontrado.")
        return None
    except ValueError as ve:
        if f"Worksheet named '{nombre_hoja}' not found" in str(ve) or \
           f"'{nombre_hoja}'" in str(ve):
             print(f"Error: La hoja '{nombre_hoja}' no fue encontrada en el archivo '{ruta_archivo}'.")
        else:
            print(f"Error de valor al procesar el Excel: {ve}")
        return None
    except Exception as e:
        print(f"Error inesperado al leer y filtrar el archivo Excel: {e}")
        # (Para depuración más profunda, puedes añadir traceback)
        # import traceback
        # print(traceback.format_exc())
        return None