import requests
import pandas as pd
import os
import unicodedata

def quitar_acentos_griego(texto):
    """Elimina los acentos y marcas de respiración del griego antiguo para poder buscar la raíz pura."""
    texto_normalizado = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto_normalizado.upper()

def descargar_nuevo_testamento_griego():
    print("--- 📖 Descargando el Nuevo Testamento Griego Completo (SBLGNT) ---")
    url = "https://raw.githubusercontent.com/jtauber/gnt-texts/master/sblgnt.txt"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("❌ Error descargando el Nuevo Testamento.")
        return

    # Diccionario con las raíces griegas limpias de acentos
    diccionario_griego = {
        "AUTORIDAD": ["ΔΕΞΙΟΣ", "ΔΕΞΙΟΝ", "ΔΕΞΙΑ", "ΔΕΞΙΟΥΣ", "ΔΕΞΙΩΝ"], 
        "CAOS": ["ΕΥΩΝΥΜΟΣ", "ΕΥΩΝΥΜΟΝ", "ΑΡΙΣΤΕΡΟΣ", "ΕΥΩΝΥΜΩΝ"], 
        "PERCEPCION": ["ΓΝΩΣΙΣ", "ΓΝΩΣΕΩΣ", "ΓΝΩΣΙΝ"], 
        "SEPARACION": ["ΣΧΙΣΜΑ", "ΣΧΙΣΜΑΤΑ"] 
    }

    lineas = response.text.split('\n')
    filas_datos = []
    
    for linea in lineas:
        if not linea.strip(): continue
        
        # Formato del archivo SBLGNT: "Libro Capitulo:Versiculo Texto..."
        partes = linea.split(' ', 2)
        if len(partes) < 3: continue
        
        libro = partes[0]
        cap_vers = partes[1].split(':')
        capitulo = cap_vers[0]
        versiculo = cap_vers[1] if len(cap_vers) > 1 else "1"
        texto_griego = partes[2]
        
        # Limpiar para buscar la raíz
        texto_limpio = quitar_acentos_griego(texto_griego)
        
        conceptos = []
        for concepto, raices in diccionario_griego.items():
            if any(raiz in texto_limpio for raiz in raices):
                conceptos.append(concepto)
                
        filas_datos.append({
            "Libro": f"NT_{libro}",
            "Capitulo": capitulo,
            "Versiculo": versiculo,
            "Hebreo_Limpio": texto_griego, 
            "Traduccion": "Texto Original Koiné",
            "Conceptos_Matriz": ", ".join(conceptos) if conceptos else "Ninguno"
        })

    df = pd.DataFrame(filas_datos)
    ruta = "../../data/processed/Libro_NT_Griego_Completo.csv"
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    df.to_csv(ruta, index=False, encoding='utf-8-sig')
    print(f"✅ Nuevo Testamento guardado: {len(df)} versículos procesados.")
    print(f"🎯 Puntos de inyección encontrados en la Matriz: {len(df[df['Conceptos_Matriz'] != 'Ninguno'])}")

def descargar_libros_ocultistas():
    print("\n--- 👁️ Descargando Textos Esotéricos Masivos (Proyecto Gutenberg) ---")
    
    # Repositorio oficial Gutenberg (Textos Planos Completos, miles de páginas)
    libros = {
        # John Dee: Sus diarios sobre las comunicaciones enoquianas (Operación de Control)
        "1_John_Dee_Diarios": "https://www.gutenberg.org/files/16331/16331-0.txt",
        
        # Salomon: La Clavícula (La base operativa del control de entidades)
        "2_Salomon_Clavicula": "https://www.gutenberg.org/files/25985/25985-0.txt",
        
        # Hermética: El Kybalion (Sigue siendo el mejor mapa de "leyes" del sistema)
        "3_Hermetica_Kybalion": "https://www.gutenberg.org/files/14209/14209-0.txt"
    }
    
    directorio_raw = "../../data/raw/esoteric/"
    os.makedirs(directorio_raw, exist_ok=True)
    
    url = "https://raw.githubusercontent.com/jtauber/gnt-texts/master/sblgnt.txt"
    # Esto engaña al firewall para que crea que es un navegador Chrome
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    
    for nombre, url in libros.items():
        ruta_archivo = os.path.join(directorio_raw, f"{nombre}.txt")
        if os.path.exists(ruta_archivo):
            print(f"⏩ {nombre} ya existe en tu disco. Saltando...")
            continue
            
        print(f"Descargando {nombre}...")
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                with open(ruta_archivo, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(resp.text)
                print(f"✅ {nombre} guardado exitosamente en data/raw/esoteric/.")
            else:
                print(f"❌ Error {resp.status_code} al descargar {nombre}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    descargar_nuevo_testamento_griego()
    descargar_libros_ocultistas()
