import json
import os
import re
import pandas as pd

def limpiar_hebreo(texto):
    """
    El hebreo masorético viene con vocales y marcas de cantilación.
    Esta función las elimina para dejar solo la raíz de las letras (consonantes),
    lo que permite que el algoritmo encuentre las palabras exactas sin margen de error.
    """
    # Rango Unicode para marcas vocálicas y de cantilación hebreas
    return re.sub(r'[\u0591-\u05C7]', '', texto)

def procesar_manuscrito(libro, capitulo):
    ruta_cruda = f"../../data/raw/{libro}_{capitulo}.json"
    ruta_procesada = f"../../data/processed/{libro}_{capitulo}_analisis.csv"
    
    print(f"Abriendo manuscrito de {libro} {capitulo}...")
    
    try:
        with open(ruta_cruda, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            
        textos_hebreos = datos.get("hebreo", [])
        textos_ingles = datos.get("traduccion_base", [])
        
        # Nuestro diccionario de variables del sistema
        # Definimos las raíces en hebreo puro (sin vocales)
        diccionario_matriz = {
            "Control/Derecha (Yamin)": "ימין",
            "Caos/Izquierda (Smol)": "שמאל",
            "Percepción (Yada)": "ידע",
            "Separación (Beyn)": "בין"
        }
        
        filas_datos = []
        
        # Iteramos sobre cada versículo
        for i, (heb, ing) in enumerate(zip(textos_hebreos, textos_ingles)):
            versiculo = i + 1
            heb_limpio = limpiar_hebreo(heb)
            
            # Buscamos si alguna variable de nuestra matriz aparece en este versículo
            conceptos_encontrados = []
            for concepto, raiz in diccionario_matriz.items():
                if raiz in heb_limpio:
                    conceptos_encontrados.append(concepto)
            
            # Guardamos la fila estructurada
            filas_datos.append({
                "Versiculo": versiculo,
                "Hebreo_Original": heb,
                "Hebreo_Limpio": heb_limpio,
                "Traduccion": re.sub(r'<[^>]+>', '', ing), # Limpiamos etiquetas HTML ocultas
                "Conceptos_Matriz": ", ".join(conceptos_encontrados) if conceptos_encontrados else "Ninguno"
            })
            
        # Convertimos todo a un DataFrame (tabla estructurada) y lo guardamos como CSV
        df = pd.DataFrame(filas_datos)
        
        # Aseguramos que el directorio exista
        os.makedirs(os.path.dirname(ruta_procesada), exist_ok=True)
        df.to_csv(ruta_procesada, index=False, encoding='utf-8-sig')
        
        print(f"¡Procesamiento completo! Análisis guardado en: {ruta_procesada}")
        
        # Mostramos un resumen rápido en la consola
        print("\n--- Resumen de Hallazgos en la Matriz ---")
        hallazgos = df[df['Conceptos_Matriz'] != "Ninguno"]
        if not hallazgos.empty:
            for index, row in hallazgos.iterrows():
                print(f"Versículo {row['Versiculo']}: Encontrado -> {row['Conceptos_Matriz']}")
        else:
            print("No se detectaron conceptos de la matriz en este capítulo.")
            
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo crudo en {ruta_cruda}. Asegurate de correr el extractor primero.")

if __name__ == "__main__":
    procesar_manuscrito("Jonah", "4")
