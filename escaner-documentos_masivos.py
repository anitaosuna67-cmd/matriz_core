import os
import openpyxl
import pandas as pd
import spacy

# Cargar el modelo multilingüe (solo para separar oraciones)
nlp = spacy.load("xx_ent_wiki_sm")
nlp.max_length = 15000000
nlp.add_pipe('sentencizer')

# Diccionario explícito bilingüe (Rápido y sin advertencias de vectores)
diccionario_cruce = {
    "DERECHA (Control)": [
        "centralización", "centralization", "monopolio", "monopoly", 
        "vigilancia", "surveillance", "piramidal", "pyramidal", 
        "jerarquía", "hierarchy", "imperio", "empire", "autoridad", "authority", "decreto"
    ],
    "IZQUIERDA (Caos)": [
        "modificación", "modification", "hibridación", "hybridization", 
        "disolución", "dissolution", "entropía", "entropy", "mutación", "mutation", "caos", "chaos"
    ]
}

def escanear_texto(directorio_raw, ruta_excel_destino, tipo_vector):
    print(f"\n--- Escaneando documentos en: {directorio_raw} ---")
    
    # SOLUCIÓN AL ERROR FATAL: Crea la carpeta si no existe para que no crashee
    os.makedirs(directorio_raw, exist_ok=True)
    
    hallazgos = []
    archivos = [f for f in os.listdir(directorio_raw) if f.endswith('.txt')]
    
    if not archivos:
        print(f"📁 Carpeta {directorio_raw} vacía. Saltando...")
        return

    for archivo in archivos:
        print(f"Analizando: {archivo}...")
        ruta_doc = os.path.join(directorio_raw, archivo)
        
        with open(ruta_doc, 'r', encoding='utf-8', errors='ignore') as f:
            texto = f.read()
            
        # SpaCy divide los 11 millones de caracteres en oraciones perfectas
        doc = nlp(texto)
        
        for sent in doc.sents:
            oracion_limpia = sent.text.lower()
            
            # Buscamos coincidencias en nuestro diccionario
            for faccion, palabras_clave in diccionario_cruce.items():
                if any(palabra in oracion_limpia for palabra in palabras_clave):
                    hallazgos.append({
                        "Origen": archivo,
                        "Tipo": "Extracción de Concepto",
                        "Operacion": faccion,
                        "Texto": sent.text.strip().replace('\n', ' ') # Limpiamos saltos de línea
                    })
                    break # Pasa a la siguiente oración si ya encontró coincidencia

    if hallazgos:
        df = pd.DataFrame(hallazgos)
        if os.path.exists(ruta_excel_destino):
            wb = openpyxl.load_workbook(ruta_excel_destino)
            ws = wb.active
        else:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(["Origen", "Ubicacion", "Tipo", "Operacion", "Faccion", "Descripcion"])
        
        for _, h in df.iterrows():
            ws.append([h["Origen"], "N/A", h["Tipo"], h["Operacion"], h["Operacion"], h["Texto"]])
        
        wb.save(ruta_excel_destino)
        print(f"✨ Se detectaron {len(hallazgos)} correlaciones nuevas.")
    else:
        print("☕ No se detectaron correlaciones en estos textos.")

if __name__ == "__main__":
    escanear_texto("data/raw/esoteric/", "data/processed/Vector_1_Esoterico.xlsx", "esoterico")
    escanear_texto("data/raw/control/", "data/processed/Vector_2_Geopolitico.xlsx", "control")
