# src/main.py

# Para asegurar que los imports relativos funcionen si ejecutas `python src/main.py`
# desde el directorio raíz del proyecto.
# Si ejecutas con `python -m src.main`, este bloque no es estrictamente necesario
# pero no hace daño.
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # src
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # facturacion_medica_bot
sys.path.append(PROJECT_ROOT)

from src.excel_handler.reader import leer_excel_muestra


def ejecutar_prueba_lectura_excel():
    """
    Define los parámetros y ejecuta la prueba de lectura del archivo Excel.
    """
    # Parámetros para la prueba
    # Asegúrate de que la ruta sea correcta desde donde ejecutas el script.
    # Si ejecutas desde 'facturacion_medica_bot', esta ruta es correcta.
    archivo_excel = "data/input/archivo-de-prueba-1.xlsx"
    nombre_hoja_proced = "Proced" # Nombre de la hoja como se discutió
    fila_encabezados_excel = 6    # La fila 6 en Excel
    fila_encabezados_idx = fila_encabezados_excel - 1 # Convertir a 0-indexed para pandas (5)
    num_filas_a_leer = 2

    print(">>> INICIANDO PRUEBA DE LECTURA DE EXCEL <<<")

    encabezados, datos_muestra = leer_excel_muestra(
        ruta_archivo=archivo_excel,
        nombre_hoja=nombre_hoja_proced,
        fila_encabezados_idx=fila_encabezados_idx,
        num_filas_datos=num_filas_a_leer
    )

    if encabezados is not None and datos_muestra is not None:
        print("\n>>> RESULTADOS DE LA PRUEBA <<<")
        print(f"Total de encabezados encontrados: {len(encabezados)}")
        print(f"Total de filas de datos leídas: {len(datos_muestra)}")
        
        if len(datos_muestra) < num_filas_a_leer and len(datos_muestra) > 0:
            print(f"Advertencia: Se solicitaron {num_filas_a_leer} filas de datos, pero solo se encontraron {len(datos_muestra)} (puede que el archivo tenga menos datos después del encabezado).")
        elif not datos_muestra and num_filas_a_leer > 0:
             print(f"Advertencia: Se solicitaron {num_filas_a_leer} filas de datos, pero no se encontró ninguna. Verifique el archivo y la configuración.")

    else:
        print("\n>>> PRUEBA DE LECTURA DE EXCEL FALLIDA O INTERRUMPIDA <<<")

    print("\n>>> PRUEBA DE LECTURA DE EXCEL FINALIZADA <<<")

if __name__ == "__main__":
    ejecutar_prueba_lectura_excel()