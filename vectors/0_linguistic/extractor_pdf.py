import PyPDF2
import os

# Rutas de los archivos usando tu estructura exacta de carpetas
ruta_pdf = "../../data/raw/esoteric/b24884431.pdf" 
ruta_txt = "../../data/raw/esoteric/La_Llave_Mayor_Salomon.txt"

print("Iniciando extracción profunda del grimorio...")

try:
    with open(ruta_pdf, "rb") as archivo_pdf:
        lector = PyPDF2.PdfReader(archivo_pdf)
        texto_completo = ""
        
        # Extraer página por página
        for i, pagina in enumerate(lector.pages):
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                texto_completo += f"\n\n--- PÁGINA {i+1} ---\n\n"
                texto_completo += texto_extraido

    # Guardar en la carpeta esoteric como un archivo .txt
    with open(ruta_txt, "w", encoding="utf-8") as archivo_txt:
        archivo_txt.write(texto_completo)

    print(f"¡Éxito! El manual ha sido decodificado y guardado en:\n{ruta_txt}")

except FileNotFoundError:
    print("Error: No se encontró el archivo PDF.")
    print(f"Asegúrate de que el PDF esté guardado exactamente en la ruta: {ruta_pdf}")
