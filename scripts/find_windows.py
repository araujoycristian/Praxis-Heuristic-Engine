#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
find_windows.py

Un script de utilidad para desarrolladores que descubre e imprime los títulos
de todas las ventanas visibles en el escritorio de Windows.

Este script es una herramienta de diagnóstico, no forma parte del flujo principal
de la aplicación. Su objetivo es ayudar a obtener el título exacto de una ventana
para usarlo en los archivos de configuración (.ini) del bot de automatización.

Dependencias:
- pywinauto (debe estar instalado en el entorno de desarrollo)

Uso:
- Activa tu entorno virtual.
- Ejecuta el script desde la terminal con: python scripts/find_windows.py
"""
import sys

def find_and_print_windows():
    """
    Busca todas las ventanas de nivel superior, filtra las visibles y con
    título, y las imprime de forma ordenada en la consola.
    """
    if sys.platform != 'win32':
        print("Este script está diseñado para ejecutarse únicamente en Windows.")
        return

    try:
        from pywinauto.desktop import Desktop
    except ImportError:
        print("\nError: La librería 'pywinauto' no está instalada.")
        print("Por favor, instálala en tu entorno virtual con: pip install pywinauto")
        return

    print("======================================================")
    print("      Buscando títulos de ventanas visibles...       ")
    print("======================================================")

    try:
        # Usamos una list comprehension para recolectar los títulos.
        # Es una forma más concisa y eficiente de crear una lista.
        visible_window_titles = [
            win.window_text()
            for win in Desktop(backend='uia').windows()
            if win.is_visible() and win.window_text()
        ]

        if not visible_window_titles:
            print("\nNo se encontraron ventanas visibles con título.")
        else:
            print(f"\nSe encontraron {len(visible_window_titles)} ventanas:\n")
            # Iteramos sobre la lista ya filtrada para imprimirla.
            for title in sorted(visible_window_titles):
                print(f"  - '{title}'")

    except Exception as e:
        print(f"\nOcurrió un error inesperado durante la búsqueda: {e}")
        print("Asegúrate de tener los permisos necesarios para inspeccionar las ventanas.")

    finally:
        print("\n======================================================")
        print("                 Búsqueda completada.                 ")
        print("======================================================")


if __name__ == "__main__":
    find_and_print_windows()