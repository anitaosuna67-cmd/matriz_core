import requests
import json
import os
import re
import time
import pandas as pd

def limpiar_hebreo(texto):
    """Elimina vocales y marcas de cantilación del hebreo masorético."""
    if not isinstance(texto, str):
        return ""
    return re.sub(r'[\u0591-\u05C7]', '', texto)

def extraer_libro_completo(libro, total_capitulos):
    """
    Descarga un libro completo, iterando capítulo por capítulo con pausas
    para no saturar la API, y lo guarda estructurado en un CSV.
    """
    print(f"\n--- Iniciando extracción masiva de: {libro} ---")
    
    diccionario_matriz = {
        "Control/Derecha (Yamin)": "ימין",
        "Caos/Izquierda (Smol)": "שמאל",
        "Percepción (Yada)": "ידע",
        "Separación (Beyn)": "בין"
    }
    
    filas_datos = []
    
    for capitulo in range(1, total_capitulos + 1):
        url = f"https://www.sefaria.org/api/texts/{libro}.{capitulo}?context=0"
        print(f"Descargando {libro} Capítulo {capitulo}...")
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Error {response.status_code} en capítulo {capitulo}. Saltando...")
                continue
                
            datos = response.json()
            textos_hebreos = datos.get("he", [])
            textos_ingles = datos.get("text", [])
            
            # Asegurar que ambas listas tengan el mismo tamaño
            max_len = max(len(textos_hebreos), len(textos_ingles))
            textos_hebreos += [""] * (max_len - len(textos_hebreos))
            textos_ingles += [""] * (max_len - len(textos_ingles))
            
            for i, (heb, ing) in enumerate(zip(textos_hebreos, textos_ingles)):
                heb_limpio = limpiar_hebreo(heb)
                
                conceptos_encontrados = []
                for concepto, raiz in diccionario_matriz.items():
                    if raiz in heb_limpio:
                        conceptos_encontrados.append(concepto)
                
                # Limpiar el inglés de etiquetas HTML
                ing_limpio = re.sub(r'<[^>]+>', '', ing) if isinstance(ing, str) else ""
                
                filas_datos.append({
                    "Libro": libro,
                    "Capitulo": capitulo,
                    "Versiculo": i + 1,
                    "Hebreo_Limpio": heb_limpio,
                    "Traduccion": ing_limpio,
                    "Conceptos_Matriz": ", ".join(conceptos_encontrados) if conceptos_encontrados else "Ninguno"
                })
            
            # PAUSA DE SEGURIDAD: 1 segundo entre capítulos para evitar bloqueos
            time.sleep(1)
            
        except Exception as e:
            print(f"Falla crítica en {libro} {capitulo}: {e}")
            
    # Guardar el libro completo en un CSV
    df = pd.DataFrame(filas_datos)
    ruta_guardado = f"../../data/processed/Libro_{libro}_Completo.csv"
    os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
    df.to_csv(ruta_guardado, index=False, encoding='utf-8-sig')
    
    total_alertas = len(df[df['Conceptos_Matriz'] != "Ninguno"])
    print(f"¡Éxito! {libro} guardado en {ruta_guardado}")
    print(f"Total de versículos procesados: {len(df)}")
    print(f"Raíces de la matriz detectadas: {total_alertas}")

if __name__ == "__main__":
    # Diccionario de libros a extraer y su cantidad de capítulos.
    # Empezamos con el diseño original (Génesis) y la estructura imperial (Daniel).
    # Podés agregar todos los libros del Tanaj a esta lista.
    biblioteca = {
        "Genesis": 50,
        "Daniel": 12,
        "Exodus": 40
    }
    
    print("Iniciando motor de rastreo de Sefaria API...")
    for nombre_libro, caps in biblioteca.items():
        extraer_libro_completo(nombre_libro, caps)
