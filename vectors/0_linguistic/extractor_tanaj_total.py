import requests
import json
import os
import re
import time
import pandas as pd

def limpiar_hebreo(texto):
    if not isinstance(texto, str): return ""
    return re.sub(r'[\u0591-\u05C7]', '', texto)

def extraer_biblioteca_completa(libros_dict):
    diccionario_matriz = {
        "Control/Derecha (Yamin)": "ימין",
        "Caos/Izquierda (Smol)": "שמאל",
        "Percepción (Yada)": "ידע",
        "Separación (Beyn)": "בין"
    }
    
    # Engañamos al servidor para que crea que somos un navegador Chrome, no un bot
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for libro, total_capitulos in libros_dict.items():
        ruta_guardado = f"../../data/processed/Libro_{libro}_Completo.csv"
        if os.path.exists(ruta_guardado):
            print(f"⏩ {libro} ya procesado. Saltando...")
            continue
            
        print(f"\n--- Descargando Corpus: {libro} ({total_capitulos} caps) ---")
        filas_datos = []
        
        for capitulo in range(1, total_capitulos + 1):
            url = f"https://www.sefaria.org/api/texts/{libro}.{capitulo}?context=0"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200: continue
                
                datos = response.json()
                textos_hebreos = datos.get("he", [])
                textos_ingles = datos.get("text", [])
                
                max_len = max(len(textos_hebreos), len(textos_ingles))
                textos_hebreos += [""] * (max_len - len(textos_hebreos))
                textos_ingles += [""] * (max_len - len(textos_ingles))
                
                for i, (heb, ing) in enumerate(zip(textos_hebreos, textos_ingles)):
                    heb_limpio = limpiar_hebreo(heb)
                    conceptos = [c for c, r in diccionario_matriz.items() if r in heb_limpio]
                    ing_limpio = re.sub(r'<[^>]+>', '', ing) if isinstance(ing, str) else ""
                    
                    filas_datos.append({
                        "Libro": libro, "Capitulo": capitulo, "Versiculo": i + 1,
                        "Hebreo_Limpio": heb_limpio, "Traduccion": ing_limpio,
                        "Conceptos_Matriz": ", ".join(conceptos) if conceptos else "Ninguno"
                    })
                time.sleep(1) # Reduje a 1 segundo porque ahora usamos Headers
            except Exception as e:
                print(f"Error en {libro} {capitulo}: {e}")
                
        if filas_datos:
            pd.DataFrame(filas_datos).to_csv(ruta_guardado, index=False, encoding='utf-8-sig')
            print(f"💾 Guardado: {libro}")

if __name__ == "__main__":
    # Agregué Genesis y Exodus al principio de la lista
    tanaj = {
        "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34, 
        "Joshua": 24, "Judges": 21, "I_Samuel": 31, "II_Samuel": 24, "I_Kings": 22, 
        "II_Kings": 25, "Isaiah": 66, "Jeremiah": 52, "Ezekiel": 48, "Hosea": 14, 
        "Joel": 4, "Amos": 9, "Obadiah": 1, "Micah": 7, "Nahum": 3, "Habakkuk": 3, 
        "Zephaniah": 3, "Haggai": 2, "Zechariah": 14, "Malachi": 3, "Psalms": 150, 
        "Proverbs": 31, "Job": 42, "Song_of_Songs": 8, "Ruth": 4, "Lamentations": 5, 
        "Ecclesiastes": 12, "Esther": 10, "Ezra": 10, "Nehemiah": 13, "I_Chronicles": 29, 
        "II_Chronicles": 36
    }
    extraer_biblioteca_completa(tanaj)
