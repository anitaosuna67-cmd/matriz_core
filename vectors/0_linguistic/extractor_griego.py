import pandas as pd
import os

def inyectar_corpus_griego():
    print("Iniciando inyección de la base de datos en Griego Koiné...")
    
    # Textos clave de la Matriz en el Nuevo Testamento (Textus Receptus)
    datos_griego = [
        # APOCALIPSIS (Revelación)
        {"Libro": "Apocalipsis", "Capitulo": 13, "Versiculo": 16, 
         "Hebreo_Limpio": "ἵνα δώσουσιν αὐτοῖς χάραγμα ἐπὶ τῆς χειρὸς αὐτῶν τῆς δεξιᾶς", 
         "Traduccion": "Y hace que a todos se les ponga una marca en la mano derecha...", 
         "Conceptos_Matriz": "Control/Derecha (Dexios)"},
        {"Libro": "Apocalipsis", "Capitulo": 10, "Versiculo": 2, 
         "Hebreo_Limpio": "καὶ ἔθηκεν τὸν πόδα αὐτοῦ τὸν δεξιὸν ἐπὶ τῆς θαλάσσης, τὸν δὲ εὐώνυμον ἐπὶ τῆς γῆς", 
         "Traduccion": "Y puso su pie derecho sobre el mar, y el izquierdo sobre la tierra...", 
         "Conceptos_Matriz": "Control/Derecha (Dexios), Caos/Izquierda (Euōnymos)"},
         
        # MATEO (Separación de sistemas)
        {"Libro": "Mateo", "Capitulo": 25, "Versiculo": 33, 
         "Hebreo_Limpio": "καὶ στήσει τὰ μὲν πρόβατα ἐκ δεξιῶν αὐτοῦ τὰ δὲ ἐρίφια ἐξ εὐωνύμων", 
         "Traduccion": "Y pondrá las ovejas a su derecha, y los cabritos a su izquierda.", 
         "Conceptos_Matriz": "Control/Derecha (Dexios), Caos/Izquierda (Euōnymos)"},
        {"Libro": "Mateo", "Capitulo": 25, "Versiculo": 34, 
         "Hebreo_Limpio": "τότε ἐρεῖ ὁ βασιλεὺς τοῖς ἐκ δεξιῶν αὐτοῦ Δεῦτε...", 
         "Traduccion": "Entonces el Rey dirá a los de su derecha: Venid...", 
         "Conceptos_Matriz": "Control/Derecha (Dexios)"},
        {"Libro": "Mateo", "Capitulo": 25, "Versiculo": 41, 
         "Hebreo_Limpio": "τότε ἐρεῖ καὶ τοῖς ἐξ εὐωνύμων Πορεύεσθε ἀπ' ἐμοῦ", 
         "Traduccion": "Entonces dirá también a los de la izquierda: Apartaos de mí...", 
         "Conceptos_Matriz": "Caos/Izquierda (Euōnymos)"},
         
        # 1 CORINTIOS (División)
        {"Libro": "Corintios", "Capitulo": 12, "Versiculo": 25, 
         "Hebreo_Limpio": "ἵνα μὴ ᾖ σχίσμα ἐν τῷ σώματι", 
         "Traduccion": "Para que no haya desavenencia (cisma/separación) en el cuerpo...", 
         "Conceptos_Matriz": "Separación (Schisma)"},
         
        # 1 TIMOTEO (Falso Conocimiento)
        {"Libro": "Timoteo", "Capitulo": 6, "Versiculo": 20, 
         "Hebreo_Limpio": "ἀντιθέσεις τῆς ψευδωνύμου γνώσεως", 
         "Traduccion": "...los argumentos de la falsamente llamada ciencia (gnosis/conocimiento).", 
         "Conceptos_Matriz": "Percepción (Gnosis)"}
    ]

    # Convertir a DataFrame
    df_griego = pd.DataFrame(datos_griego)
    
    # Separar por libros para mantener la estructura de archivos masivos
    libros = df_griego["Libro"].unique()
    
    for libro in libros:
        df_libro = df_griego[df_griego["Libro"] == libro]
        # Respetamos la nomenclatura "Libro_X_Completo.csv" para que el dashboard lo lea automáticamente
        ruta_guardado = f"../../data/processed/Libro_{libro}_Griego_Completo.csv"
        os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
        df_libro.to_csv(ruta_guardado, index=False, encoding='utf-8-sig')
        print(f"✅ Extracción Koiné guardada: {ruta_guardado}")

if __name__ == "__main__":
    inyectar_corpus_griego()
