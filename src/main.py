# src/main.py

import sys
import os

# Asegurar que los imports relativos funcionen
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # src
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # facturacion_medica_bot
sys.path.append(PROJECT_ROOT)

from src.excel_handler.reader import obtener_datos_filtrados_excel
# Si quieres usar la función de muestra también, descomenta:
# from src.excel_handler.reader import leer_excel_muestra


def ejecutar_prueba_filtrado_excel():
    """
    Define los parámetros, ejecuta el filtrado del archivo Excel
    e imprime el número de filas resultantes y logs de depuración,
    filtrando para un solo usuario especificado.
    """
    # --- CONFIGURACIÓN DE PRUEBA ---
    archivo_excel = "data/input/archivo-de-prueba-1.xlsx" # Asegúrate de que este archivo exista
    nombre_hoja_proced = "Proced"
    fila_encabezados_excel = 6    # La fila 6 en Excel (1-indexed)
    fila_encabezados_idx = fila_encabezados_excel - 1 # Convertir a 0-indexed para pandas

    # --- SELECCIÓN DE USUARIO PARA ESTA EJECUCIÓN ---
    # Cambia este valor para probar con diferentes usuarios.
    # Más adelante, esto podría venir de un input, config file o argumento de línea de comandos.
    usuario_a_procesar = "NANCY" 
    # usuario_a_procesar = "SEBASTIAN" # Descomenta esta línea y comenta la anterior para probar con Sebastián

    print(f"\n*********************************************************************")
    print(f"*** ATENCIÓN: Se procesarán datos únicamente para el USUARIO: {usuario_a_procesar.upper()} ***")
    print(f"*********************************************************************\n")

    # Criterios de filtro (los nombres de columna deben coincidir EXACTAMENTE con los del Excel)
    criterios = {
        "USUARIO:": usuario_a_procesar,     # Usamos el string del usuario seleccionado
        "ES PYP:": "No",                   
        "CUPS:": 890201,                   # Se tratará como string "890201" para comparación en reader.py
        "ESPECIALIDAD:": "MEDICO GENERAL"   # Se normalizará
    }
    # -------------------------------

    print(">>> INICIANDO PRUEBA DE FILTRADO DE EXCEL <<<")

    df_filtrado = obtener_datos_filtrados_excel(
        ruta_archivo=archivo_excel,
        nombre_hoja=nombre_hoja_proced,
        fila_encabezados_idx=fila_encabezados_idx,
        criterios_filtro=criterios
    )

    if df_filtrado is not None:
        num_filas_disponibles = len(df_filtrado)
        print(f"\n>>> RESULTADOS FINALES DEL FILTRADO (para USUARIO: {usuario_a_procesar.upper()}) <<<")
        print(f"Número de filas disponibles para trabajar después de todos los filtros: {num_filas_disponibles}")
        
        if num_filas_disponibles > 0:
            print(f"Se encontraron {num_filas_disponibles} fila(s) que cumplen con todos los criterios.")
            if num_filas_disponibles < 10: # Imprimir algunas filas si son pocas para inspección
                print("\n--- Muestra de Filas Filtradas (primeras 5 o menos): ---")
                # Seleccionar solo las columnas de los criterios para una vista más limpia
                columnas_de_criterios = list(criterios.keys())
                # Asegurarse de que todas las columnas de criterios existen en el df_filtrado
                columnas_a_mostrar = [col for col in columnas_de_criterios if col in df_filtrado.columns]
                
                if columnas_a_mostrar: # Solo imprimir si hay columnas para mostrar
                    print(df_filtrado[columnas_a_mostrar].head().to_string())
                else:
                    print("No hay columnas de criterios para mostrar (esto no debería ocurrir si los filtros se aplicaron).")
                
                # Si quieres ver todas las columnas de las filas filtradas (puede ser muy ancho):
                # print("\n--- Muestra de Filas Filtradas (todas las columnas, primeras 5 o menos): ---")
                # print(df_filtrado.head().to_string())

        elif num_filas_disponibles == 0:
            print(f"No se encontraron filas que cumplan con todos los criterios especificados para el USUARIO: {usuario_a_procesar.upper()}.")
    else:
        print("\n>>> PRUEBA DE FILTRADO DE EXCEL FALLIDA O INTERRUMPIDA <<<")
        print("Verifica los mensajes de error anteriores para más detalles.")

    print("\n>>> PRUEBA DE FILTRADO DE EXCEL FINALIZADA <<<")

if __name__ == "__main__":
    ejecutar_prueba_filtrado_excel()