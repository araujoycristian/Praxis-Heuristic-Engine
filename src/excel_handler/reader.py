# src/excel_handler/reader.py

import pandas as pd

def leer_excel_muestra(ruta_archivo: str, nombre_hoja: str, fila_encabezados_idx: int, num_filas_datos: int):
    """
    Lee una muestra de un archivo Excel, extrayendo encabezados y un número específico de filas de datos.

    Args:
        ruta_archivo (str): Ruta al archivo Excel.
        nombre_hoja (str): Nombre de la hoja a leer.
        fila_encabezados_idx (int): Índice de la fila que contiene los encabezados (0-indexed).
                                    Por ejemplo, la fila 6 del Excel es el índice 5.
        num_filas_datos (int): Número de filas de datos a leer DESPUÉS de la fila de encabezados.

    Returns:
        tuple: Una tupla conteniendo (lista_de_encabezados, lista_de_diccionarios_de_datos_leidos).
               Retorna (None, None) si ocurre un error.
    """
    print(f"--- Iniciando lectura del archivo: {ruta_archivo} ---")
    try:
        # pandas.read_excel:
        # - sheet_name: especifica la hoja a leer.
        # - header: especifica la fila (0-indexed) a usar como encabezados de columna.
        #           Las filas anteriores a esta serán omitidas de los datos del DataFrame.
        # - nrows: especifica el número de filas de *datos* a leer DESPUÉS de la fila de encabezado.
        df = pd.read_excel(
            ruta_archivo,
            sheet_name=nombre_hoja,
            header=fila_encabezados_idx,
            nrows=num_filas_datos,
            engine='openpyxl' # Es bueno especificar el motor, especialmente si hay problemas de compatibilidad
        )

        # Obtener los encabezados de las columnas del DataFrame resultante
        encabezados = df.columns.tolist()
        print("\n--- Encabezados Detectados ---")
        if not encabezados:
            print("No se detectaron encabezados. Verifica la configuración de 'fila_encabezados_idx'.")
        else:
            for i, encabezado in enumerate(encabezados):
                print(f"  {i+1}. {encabezado}")

        # Convertir las filas de datos del DataFrame a una lista de diccionarios
        # donde cada diccionario representa una fila.
        datos_pacientes = df.to_dict(orient='records')

        print(f"\n--- {len(datos_pacientes)} Primera(s) Fila(s) de Datos Leídas ---")
        if not datos_pacientes:
            print("No se encontraron datos de pacientes con los parámetros dados (o nrows=0).")
        else:
            for i, paciente_data in enumerate(datos_pacientes):
                # La fila del Excel sería fila_encabezados_idx (para la fila de encabezados)
                # + 1 (para convertir de 0-indexed a 1-indexed)
                # + i (índice de la fila de datos actual, 0-indexed)
                # + 1 (para la primera fila de datos después del encabezado)
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
        # pandas puede lanzar ValueError si la hoja no existe con algunos motores.
        # Con openpyxl, podría ser un KeyError o similar si la hoja no se encuentra.
        # Es mejor verificar el mensaje de error específico.
        if f"Worksheet named '{nombre_hoja}' not found" in str(ve) or \
           f"'{nombre_hoja}'" in str(ve): # Captura más genérica para errores de hoja no encontrada
             print(f"Error: La hoja '{nombre_hoja}' no fue encontrada en el archivo '{ruta_archivo}'.")
        else:
            print(f"Error de valor al procesar el Excel: {ve}")
        return None, None
    except Exception as e:
        print(f"Error inesperado al leer el archivo Excel: {e}")
        return None, None