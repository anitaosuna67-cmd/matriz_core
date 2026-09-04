import requests
import json
import os

def extraer_texto_sefaria(libro, capitulo):
    """
    Se conecta a la API de Sefaria y extrae un capítulo completo.
    """
    # La URL estructurada de la API
    url = f"https://www.sefaria.org/api/texts/{libro}.{capitulo}?context=0"
    
    print(f"Iniciando extracción de {libro} Capítulo {capitulo}...")
    
    try:
        # Hacemos la petición a la API
        response = requests.get(url)
        response.raise_for_status() # Verifica que no haya errores de conexión
        
        datos = response.json()
        
        # Filtramos solo lo que nos importa
        texto_hebreo = datos.get("he", [])
        texto_ingles = datos.get("text", []) # Sefaria devuelve la traducción base en inglés
        
        resultado = {
            "referencia": f"{libro} {capitulo}",
            "hebreo": texto_hebreo,
            "traduccion_base": texto_ingles
        }
        
        # Guardamos el JSON crudo en nuestra carpeta de datos
        ruta_guardado = f"../../data/raw/{libro}_{capitulo}.json"
        
        # Aseguramos que el directorio exista
        os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
        
        with open(ruta_guardado, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)
            
        print(f"¡Éxito! Datos guardados en {ruta_guardado}")
        return resultado

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return None

# Prueba del sistema con Jonás 4
if __name__ == "__main__":
    extraer_texto_sefaria("Jonah", "4")
