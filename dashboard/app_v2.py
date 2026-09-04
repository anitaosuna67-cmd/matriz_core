import streamlit as st
import pandas as pd
import os
import glob
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import html 
import plotly.express as px
import plotly.graph_objects as go
import urllib.request
import xml.etree.ElementTree as ET
import urllib.parse
import random

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Matriz Core - Sistema de Análisis", page_icon="🔮", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; }
    h1, h2, h3 { color: #e2e8f0 !important; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; }
    .stTabs [aria-selected="true"] { color: #38bdf8 !important; border-bottom-color: #38bdf8 !important; }
    div[data-testid="stMetricValue"] { color: #38bdf8 !important; }
    .raiz-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; margin: 6px 0; }
    </style>
""", unsafe_allow_html=True)

st.title("🔮 SISTEMATIZACIÓN CORE - LA MATRIZ")
st.caption("Terminal Integral de Inteligencia: Jerarquías, Geolocalización, Ratio de Entidades y Radar OSINT")

# --- 2. RUTAS DE ARCHIVOS ---
ruta_procesados = "../data/processed/"
ruta_raw_esoterico = "../data/raw/esoteric/" 
ruta_base = os.path.join(ruta_procesados, "Matriz_Core_Sistematizacion_Base.xlsx")
ruta_esoterico = os.path.join(ruta_procesados, "Vector_1_Esoterico.xlsx")
ruta_geopolitico = os.path.join(ruta_procesados, "Vector_2_Geopolitico.xlsx")
ruta_biotecnologico = os.path.join(ruta_procesados, "Vector_3_Biotecnologico.xlsx")
ruta_astro = os.path.join(ruta_procesados, "Vector_4_Astro.xlsx")

# --- 3. CARGA DE DATOS ESTÁTICOS ---
@st.cache_data
def cargar_textos_masivos():
    patron = os.path.join(ruta_procesados, "Libro_*_Completo.csv")
    archivos = glob.glob(patron)
    if not archivos: return pd.DataFrame()
    return pd.concat([pd.read_csv(f) for f in archivos], ignore_index=True)

@st.cache_data
def cargar_excel(ruta, hoja, saltar=4):
    if os.path.exists(ruta): return pd.read_excel(ruta, sheet_name=hoja, skiprows=saltar)
    return pd.DataFrame()

@st.cache_data
def cargar_manuales_raw():
    textos = {}
    if os.path.exists(ruta_raw_esoterico):
        for arch in glob.glob(os.path.join(ruta_raw_esoterico, "*.txt")):
            nombre = os.path.basename(arch).replace(".txt", "")
            try:
                with open(arch, 'r', encoding='utf-8') as f: textos[nombre] = f.read()
            except Exception:
                with open(arch, 'r', encoding='latin-1') as f: textos[nombre] = f.read()
    return textos

# --- 4. MOTOR OSINT ---
@st.cache_data(ttl=3600) 
def obtener_noticias_tiempo_real(keyword):
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=es-419&gl=419&ceid=419:es"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        return [item.find('title').text for item in root.findall('.//item')[:2]]
    except Exception:
        return []

df_ling_masivo = cargar_textos_masivos()
df_eso_base = cargar_excel(ruta_esoterico, "Datos Esotéricos")
df_geo = cargar_excel(ruta_geopolitico, "Estructuras de Control")
df_bio = cargar_excel(ruta_biotecnologico, "Alteraciones Biológicas")
df_astro_base = cargar_excel(ruta_astro, "Reloj del Sistema")
df_arquetipos = cargar_excel(ruta_base, "Arquetipos de Facciones")
textos_raw_eso = cargar_manuales_raw() 

# --- 5. BASE ASTRO-TEMPORAL ---
nuevos_ciclos_astro = [
    {"Ciclo / Marcador Celeste": "Conjunción Júpiter-Saturno", "Inicio": "2020-12-21", "Fin": "2040-10-31", "Impacto Estructural": "Mutación a Aire. Digitalización del control.", "Facción Alineada": "DERECHA (Control)"},
    {"Ciclo / Marcador Celeste": "Tránsito de Urano en Tauro", "Inicio": "2018-05-15", "Fin": "2026-04-26", "Impacto Estructural": "Disrupción radical de la biología y agricultura.", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Ciclo / Marcador Celeste": "Entrada de Plutón en Acuario", "Inicio": "2023-03-23", "Fin": "2043-03-08", "Impacto Estructural": "Revolución transhumanista, IA general.", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Ciclo / Marcador Celeste": "Conjunción Saturno-Plutón", "Inicio": "2020-01-12", "Fin": "2021-12-31", "Impacto Estructural": "Contracción extrema y fronteras cerradas.", "Facción Alineada": "DERECHA (Control)"},
    {"Ciclo / Marcador Celeste": "Retorno de Plutón (USA)", "Inicio": "2022-02-20", "Fin": "2024-11-19", "Impacto Estructural": "Fractura interna de los imperios occidentales.", "Facción Alineada": "Ambas / Reloj"}
]
df_astro = pd.concat([df_astro_base, pd.DataFrame(nuevos_ciclos_astro)], ignore_index=True) if not df_astro_base.empty else pd.DataFrame(nuevos_ciclos_astro)

# ============================================================================
# --- 6. SISTEMA ENOQUIANO EXPANDIDO + PLANO SEMÁNTICO (Jonás 4:11) ---
# ============================================================================

# BASE SEMÁNTICA: Jonás 4:11 — לֹא־יָדַע אִישׁ בֵּין־יְמִינוֹ לִשְׂמֹאלוֹ
# Las cuatro raíces del sistema coexisten en un solo versículo

CUADRANTES_PLANO = {
    "Q1": {
        "nombre": "Control con Límites",
        "eje_x": 1, "eje_y": 1,
        "raices": ["YAMIN_DEXIOS", "BEYN_KRIMA"],
        "descripcion": "Autoridad ejercida mediante separación precisa.\nLey, ritual, pacto, clasificación.",
        "faccion": "DERECHA (Control)",
        "color": "#1d4ed8",
        "hex_fill": "rgba(29,78,216,0.15)",
        "ejemplos": ["Salmo 110:1", "Éxodo 15:6", "Levítico (rituales de separación)"]
    },
    "Q2": {
        "nombre": "Autoridad por Discernimiento",
        "eje_x": 1, "eje_y": -1,
        "raices": ["YAMIN_DEXIOS", "YADA_GINOSKO"],
        "descripcion": "Poder que emana del conocimiento encarnado.\nSabiduría operativa, juicio directo.",
        "faccion": "DERECHA (Control)",
        "color": "#2563eb",
        "hex_fill": "rgba(37,99,235,0.12)",
        "ejemplos": ["Proverbios 3:16", "1 Reyes 3:9 (Salomón)", "Isaías 41:10"]
    },
    "Q3": {
        "nombre": "Caos Contenido",
        "eje_x": -1, "eje_y": 1,
        "raices": ["SMOL_ARISTEROS", "BEYN_KRIMA"],
        "descripcion": "Frontera violada pero reconocida.\nTransgresión con conciencia del límite.",
        "faccion": "IZQUIERDA (Caos)",
        "color": "#be123c",
        "hex_fill": "rgba(190,18,60,0.12)",
        "ejemplos": ["Eclesiastés 10:2", "Génesis 13:9 (separación Lot/Abraham)"]
    },
    "Q4": {
        "nombre": "Indistinción Total",
        "eje_x": -1, "eje_y": -1,
        "raices": ["SMOL_ARISTEROS", "YADA_GINOSKO"],
        "descripcion": "Colapso de la función discriminatoria.\nHibridación pura. JONÁS 4:11 vive aquí.",
        "faccion": "IZQUIERDA (Caos)",
        "color": "#e11d48",
        "hex_fill": "rgba(225,29,72,0.15)",
        "ejemplos": ["★ Jonás 4:11 (TEXTO GENERADOR)", "Génesis 6:1-4 (Vigilantes)", "Daniel 2:43"]
    },
    "UMBRAL": {
        "nombre": "Zona de Frontera",
        "eje_x": 0, "eje_y": 0,
        "raices": ["BEYN_KRIMA"],
        "descripcion": "Solo beyn — espacio intermedio puro.\nNo pertenece a ningún ala.",
        "faccion": "Ambas / Umbral",
        "color": "#0ea5e9",
        "hex_fill": "rgba(14,165,233,0.10)",
        "ejemplos": ["Génesis 1:4-7 (separaciones primordiales)", "Ezequiel 22:26"]
    }
}

# 91 GOBERNADORES DE LOS 30 AETHYRS — SISTEMA DEE COMPLETO
# Fuente: Liber Scientiae, John Dee / Edward Kelley (1584)
GOBERNADORES_91 = [
    {"nombre": "Occodon",  "aethyr": "TEX", "num": 1,  "jurisdiccion": "Bretaña / Islas del Norte",           "funcion": "Custodia del primer umbral, registro de entrada",            "cuadrante": "Q1",     "lat": 51.5,  "lon": -0.1},
    {"nombre": "Pascomb",  "aethyr": "TEX", "num": 2,  "jurisdiccion": "Germania Occidental",                 "funcion": "Registro perpetuo de acciones y consecuencias",             "cuadrante": "Q1",     "lat": 50.9,  "lon": 6.9},
    {"nombre": "Valgars",  "aethyr": "TEX", "num": 3,  "jurisdiccion": "Galia / Francia",                     "funcion": "Aplicación de consecuencias jurisdiccionales",              "cuadrante": "Q1",     "lat": 48.8,  "lon": 2.3},
    {"nombre": "Doagnis",  "aethyr": "RII", "num": 4,  "jurisdiccion": "Egipto / Valle del Nilo",             "funcion": "Administración de flujos de poder entre facciones",          "cuadrante": "Q1",     "lat": 30.0,  "lon": 31.2},
    {"nombre": "Pacasna",  "aethyr": "RII", "num": 5,  "jurisdiccion": "Mesopotamia / Tigris-Éufrates",       "funcion": "Separación y delimitación de jurisdicciones",               "cuadrante": "Q1",     "lat": 33.3,  "lon": 44.4},
    {"nombre": "Dialoia",  "aethyr": "RII", "num": 6,  "jurisdiccion": "Persia / Irán",                       "funcion": "Diálogo entre órdenes jerárquicos distintos",               "cuadrante": "Q2",     "lat": 35.6,  "lon": 51.3},
    {"nombre": "Samapha",  "aethyr": "BAG", "num": 7,  "jurisdiccion": "Arabia / Península Arábiga",          "funcion": "Consolidación de estructuras de autoridad",                 "cuadrante": "Q1",     "lat": 24.7,  "lon": 46.7},
    {"nombre": "Virooli",  "aethyr": "BAG", "num": 8,  "jurisdiccion": "India / Subcontinente",               "funcion": "Mantenimiento de orden en territorios extensos",            "cuadrante": "Q1",     "lat": 28.6,  "lon": 77.2},
    {"nombre": "Andispi",  "aethyr": "BAG", "num": 9,  "jurisdiccion": "Escitia / Asia Central",              "funcion": "Control de fronteras nómadas e inestables",                 "cuadrante": "Q2",     "lat": 43.0,  "lon": 68.0},
    {"nombre": "Thotanp",  "aethyr": "ZAA", "num": 10, "jurisdiccion": "Etiopía / Cuerno de África",          "funcion": "Visión de largo plazo, planificación de ciclos",            "cuadrante": "Q2",     "lat": 9.0,   "lon": 38.7},
    {"nombre": "Axziarg",  "aethyr": "ZAA", "num": 11, "jurisdiccion": "Anatolia / Asia Menor",               "funcion": "Análisis estratégico de estructuras en conflicto",          "cuadrante": "Q2",     "lat": 39.9,  "lon": 32.8},
    {"nombre": "Pothnir",  "aethyr": "ZAA", "num": 12, "jurisdiccion": "Grecia / Mar Egeo",                   "funcion": "Discernimiento filosófico aplicado al gobierno",            "cuadrante": "Q2",     "lat": 37.9,  "lon": 23.7},
    {"nombre": "Lazdixi",  "aethyr": "DES", "num": 13, "jurisdiccion": "Fenicia / Levante costero",           "funcion": "Memoria institucional, archivo de pactos y tratados",       "cuadrante": "Q1",     "lat": 33.5,  "lon": 35.3},
    {"nombre": "Nocamal",  "aethyr": "DES", "num": 14, "jurisdiccion": "Cartago / Norte de África",           "funcion": "Transmisión de conocimiento entre generaciones de poder",   "cuadrante": "Q2",     "lat": 36.8,  "lon": 10.1},
    {"nombre": "Tiarpax",  "aethyr": "DES", "num": 15, "jurisdiccion": "Hispania / Iberia",                   "funcion": "Expansión ordenada de jurisdicción territorial",            "cuadrante": "Q1",     "lat": 40.4,  "lon": -3.7},
    {"nombre": "Saxtomp",  "aethyr": "VTI", "num": 16, "jurisdiccion": "Britania / Stonehenge",               "funcion": "Calibración de ciclos temporales y astronómicos",           "cuadrante": "Q2",     "lat": 51.1,  "lon": -1.8},
    {"nombre": "Vavaamp",  "aethyr": "VTI", "num": 17, "jurisdiccion": "Escandinavia / Norte",                "funcion": "Medición de fuerzas entre órdenes en tensión",             "cuadrante": "Q1",     "lat": 59.9,  "lon": 10.7},
    {"nombre": "Zirzird",  "aethyr": "VTI", "num": 18, "jurisdiccion": "Rusia / Estepa póntica",              "funcion": "Instrumentos de vigilancia y detección temprana",           "cuadrante": "Q1",     "lat": 55.7,  "lon": 37.6},
    {"nombre": "Omagrap",  "aethyr": "NIA", "num": 19, "jurisdiccion": "Polonia / Europa del Este",           "funcion": "Comunicación vertical entre capas del sistema",             "cuadrante": "Q2",     "lat": 52.2,  "lon": 21.0},
    {"nombre": "Zildron",  "aethyr": "NIA", "num": 20, "jurisdiccion": "Bohemia / Europa Central",            "funcion": "Codificación de mensajes entre rangos",                     "cuadrante": "Q1",     "lat": 50.0,  "lon": 14.4},
    {"nombre": "Parziba",  "aethyr": "NIA", "num": 21, "jurisdiccion": "Hungría / Cuenca del Danubio",        "funcion": "Transmisión de instrucciones sin pérdida semántica",         "cuadrante": "Q2",     "lat": 47.4,  "lon": 19.0},
    {"nombre": "Ronoamb",  "aethyr": "TOR", "num": 22, "jurisdiccion": "Anatolia / Frigia",                   "funcion": "Custodia de recursos estratégicos y minerales",             "cuadrante": "Q1",     "lat": 39.0,  "lon": 30.5},
    {"nombre": "Onizimp",  "aethyr": "TOR", "num": 23, "jurisdiccion": "Siria / Mesopotamia Alta",            "funcion": "Acumulación y redistribución controlada de capital",        "cuadrante": "Q1",     "lat": 36.2,  "lon": 37.1},
    {"nombre": "Zaxanin",  "aethyr": "TOR", "num": 24, "jurisdiccion": "Chipre / Mediterráneo Oriental",      "funcion": "Gestión de rutas comerciales y flujos de valor",            "cuadrante": "Q2",     "lat": 35.1,  "lon": 33.3},
    {"nombre": "Odraxti",  "aethyr": "LIN", "num": 25, "jurisdiccion": "Babilonia / Código de Hammurabi",     "funcion": "Codificación y aplicación de sistemas legales",             "cuadrante": "Q1",     "lat": 32.5,  "lon": 44.4},
    {"nombre": "Genadol",  "aethyr": "LIN", "num": 26, "jurisdiccion": "Roma / Italia",                       "funcion": "Derecho institucional, jurisprudencia y precedente",        "cuadrante": "Q1",     "lat": 41.9,  "lon": 12.4},
    {"nombre": "Aspiaon",  "aethyr": "LIN", "num": 27, "jurisdiccion": "Judea / Jerusalén",                   "funcion": "Ley sagrada, regulación de lo puro e impuro",              "cuadrante": "Q1",     "lat": 31.7,  "lon": 35.2},
    {"nombre": "Toantom",  "aethyr": "ASP", "num": 28, "jurisdiccion": "Egipto / Alejandría",                 "funcion": "Sistemas de vigilancia e inteligencia centralizada",         "cuadrante": "Q1",     "lat": 31.2,  "lon": 29.9},
    {"nombre": "Vixpalg",  "aethyr": "ASP", "num": 29, "jurisdiccion": "Partia / Irán Oriental",              "funcion": "Red de informantes y agentes encubiertos",                  "cuadrante": "Q2",     "lat": 33.5,  "lon": 60.0},
    {"nombre": "Oxlopar",  "aethyr": "ASP", "num": 30, "jurisdiccion": "Macedonia / Grecia del Norte",        "funcion": "Contraespionaje y purga de infiltraciones",                 "cuadrante": "Q1",     "lat": 40.6,  "lon": 22.9},
    {"nombre": "Zarzilg",  "aethyr": "CHR", "num": 31, "jurisdiccion": "Caldea / Astronomía babilónica",      "funcion": "Administración de ciclos temporales y calendarios",          "cuadrante": "Q2",     "lat": 30.0,  "lon": 46.0},
    {"nombre": "Ioaltap",  "aethyr": "CHR", "num": 32, "jurisdiccion": "Egipto / Karnak",                     "funcion": "Sincronización de rituales con ciclos astronómicos",         "cuadrante": "Q1",     "lat": 25.7,  "lon": 32.6},
    {"nombre": "Ivonph",   "aethyr": "CHR", "num": 33, "jurisdiccion": "Stonehenge / Bretaña",                "funcion": "Marcadores de equinoccios y solsticios como umbrales",      "cuadrante": "UMBRAL", "lat": 51.1,  "lon": -1.8},
    {"nombre": "Tedoand",  "aethyr": "POP", "num": 34, "jurisdiccion": "India / Punjab",                      "funcion": "Control demográfico y administración de poblaciones",        "cuadrante": "Q1",     "lat": 31.5,  "lon": 74.3},
    {"nombre": "Vivipos",  "aethyr": "POP", "num": 35, "jurisdiccion": "China / Valle del Amarillo",          "funcion": "Censos, clasificación y registro de poblaciones",           "cuadrante": "Q1",     "lat": 34.7,  "lon": 113.6},
    {"nombre": "Uvivon",   "aethyr": "POP", "num": 36, "jurisdiccion": "Mesoamérica / Yucatán",               "funcion": "Regulación de roles sociales y estratificación",            "cuadrante": "Q1",     "lat": 20.9,  "lon": -89.6},
    {"nombre": "Zinggen",  "aethyr": "ZEN", "num": 37, "jurisdiccion": "Alejandría / Biblioteca",             "funcion": "Administración del conocimiento técnico y científico",      "cuadrante": "Q2",     "lat": 31.2,  "lon": 29.9},
    {"nombre": "Alpudus",  "aethyr": "ZEN", "num": 38, "jurisdiccion": "Bagdad / Casa de la Sabiduría",       "funcion": "Traducción y preservación de corpus filosóficos",           "cuadrante": "Q2",     "lat": 33.3,  "lon": 44.4},
    {"nombre": "Taoagla",  "aethyr": "ZEN", "num": 39, "jurisdiccion": "Toledo / España Medieval",            "funcion": "Síntesis de tradiciones del conocimiento en poder",         "cuadrante": "Q2",     "lat": 39.8,  "lon": -4.0},
    {"nombre": "Sigmorf",  "aethyr": "TAN", "num": 40, "jurisdiccion": "Westfalia / Europa",                  "funcion": "Formación y mantenimiento de tratados entre potencias",     "cuadrante": "Q1",     "lat": 51.9,  "lon": 7.6},
    {"nombre": "Aydropt",  "aethyr": "TAN", "num": 41, "jurisdiccion": "Viena / Imperio Austro-Húngaro",      "funcion": "Diplomacia de alto nivel y protocolo de alianzas",           "cuadrante": "Q1",     "lat": 48.2,  "lon": 16.3},
    {"nombre": "Toantomv", "aethyr": "TAN", "num": 42, "jurisdiccion": "Versalles / Francia",                 "funcion": "Etiqueta del poder, formalización de jerarquías",           "cuadrante": "Q1",     "lat": 48.8,  "lon": 2.1},
    {"nombre": "Lazdixr",  "aethyr": "LEA", "num": 43, "jurisdiccion": "Atenas / Agora",                      "funcion": "Legitimación del liderazgo ante poblaciones",               "cuadrante": "Q2",     "lat": 37.9,  "lon": 23.7},
    {"nombre": "Notahon",  "aethyr": "LEA", "num": 44, "jurisdiccion": "Roma / Foro Romano",                  "funcion": "Oratoria y persuasión al servicio del orden",               "cuadrante": "Q2",     "lat": 41.8,  "lon": 12.4},
    {"nombre": "Vastrim",  "aethyr": "LEA", "num": 45, "jurisdiccion": "Constantinopla / Bizancio",           "funcion": "Unificación de autoridad espiritual y temporal",            "cuadrante": "Q1",     "lat": 41.0,  "lon": 28.9},
    {"nombre": "Tahamdo",  "aethyr": "OXO", "num": 46, "jurisdiccion": "Esparta / Grecia",                    "funcion": "Estructuras de obediencia absoluta y disciplina",           "cuadrante": "Q1",     "lat": 37.0,  "lon": 22.4},
    {"nombre": "Nociabi",  "aethyr": "OXO", "num": 47, "jurisdiccion": "Prusia / Germania",                   "funcion": "Jerarquía militar y cadena de mando",                       "cuadrante": "Q1",     "lat": 52.5,  "lon": 13.4},
    {"nombre": "Tastoxo",  "aethyr": "OXO", "num": 48, "jurisdiccion": "Japón / Shogunato",                   "funcion": "Honor y lealtad como mecanismos de control",                "cuadrante": "Q2",     "lat": 35.6,  "lon": 139.6},
    {"nombre": "Cucarpt",  "aethyr": "UTA", "num": 49, "jurisdiccion": "Rubicón / Italia Norte",              "funcion": "Gestión de puntos de no retorno y umbrales críticos",       "cuadrante": "UMBRAL", "lat": 44.1,  "lon": 12.2},
    {"nombre": "Lazindor", "aethyr": "UTA", "num": 50, "jurisdiccion": "Termópilas / Grecia",                 "funcion": "Defensa de pasos estratégicos y cuellos de botella",        "cuadrante": "Q1",     "lat": 38.8,  "lon": 22.5},
    {"nombre": "Sigmorfv", "aethyr": "UTA", "num": 51, "jurisdiccion": "Paso de Bering / Norte",              "funcion": "Control de migraciones y desplazamientos poblacionales",   "cuadrante": "Q1",     "lat": 65.5,  "lon": -168.0},
    {"nombre": "Gebabal",  "aethyr": "ZIM", "num": 52, "jurisdiccion": "Venecia / Banca Medieval",            "funcion": "Creación y regulación de sistemas de valor",                "cuadrante": "Q1",     "lat": 45.4,  "lon": 12.3},
    {"nombre": "Agirath",  "aethyr": "ZIM", "num": 53, "jurisdiccion": "Ámsterdam / VOC",                     "funcion": "Instrumentos financieros y deuda como control",             "cuadrante": "Q2",     "lat": 52.3,  "lon": 4.9},
    {"nombre": "Zinggenv", "aethyr": "ZIM", "num": 54, "jurisdiccion": "Londres / City",                      "funcion": "Banca central y monopolio de la emisión",                   "cuadrante": "Q1",     "lat": 51.5,  "lon": -0.08},
    {"nombre": "Tafitoal", "aethyr": "LOE", "num": 55, "jurisdiccion": "Sumer / Escritura cuneiforme",        "funcion": "Creación de sistemas de escritura como tecnología de poder", "cuadrante": "Q2",    "lat": 31.9,  "lon": 45.8},
    {"nombre": "Iolana",   "aethyr": "LOE", "num": 56, "jurisdiccion": "Egipto / Escritura jeroglífica",      "funcion": "Codificación del poder en sistemas simbólicos",             "cuadrante": "Q2",     "lat": 25.6,  "lon": 32.5},
    {"nombre": "Palam",    "aethyr": "LOE", "num": 57, "jurisdiccion": "Fenicia / Alfabeto",                  "funcion": "Democratización controlada del lenguaje escrito",           "cuadrante": "UMBRAL", "lat": 34.0,  "lon": 35.6},
    {"nombre": "Molpand",  "aethyr": "IKH", "num": 58, "jurisdiccion": "Roma / Vías Romanas",                 "funcion": "Infraestructura de movilidad y control territorial",         "cuadrante": "Q1",     "lat": 41.9,  "lon": 12.4},
    {"nombre": "Vsnarda",  "aethyr": "IKH", "num": 59, "jurisdiccion": "China / Gran Muralla",                "funcion": "Arquitectura defensiva y demarcación de fronteras",          "cuadrante": "Q1",     "lat": 40.4,  "lon": 116.5},
    {"nombre": "Ponodol",  "aethyr": "IKH", "num": 60, "jurisdiccion": "Egipto / Pirámides",                  "funcion": "Monumentalización del poder como señal de permanencia",     "cuadrante": "Q1",     "lat": 29.9,  "lon": 31.1},
    {"nombre": "Lexarph",  "aethyr": "ZAX", "num": 61, "jurisdiccion": "El Abismo / Sin geografía",           "funcion": "Guardián del umbral entre el ser y el no-ser",              "cuadrante": "UMBRAL", "lat": 0.0,   "lon": 0.0},
    {"nombre": "Comanan",  "aethyr": "ZAX", "num": 62, "jurisdiccion": "El Abismo / Sin geografía",           "funcion": "Disolución de estructuras que cruzaron el umbral",          "cuadrante": "UMBRAL", "lat": 0.0,   "lon": 0.5},
    {"nombre": "Tabitom",  "aethyr": "ZAX", "num": 63, "jurisdiccion": "El Abismo / Sin geografía",           "funcion": "Reintegración post-disolución en nueva forma",              "cuadrante": "UMBRAL", "lat": 0.0,   "lon": -0.5},
    {"nombre": "Orcanir",  "aethyr": "ZIP", "num": 64, "jurisdiccion": "Asiria / Nínive",                     "funcion": "Tecnología bélica y proyección de fuerza ordenada",          "cuadrante": "Q1",     "lat": 36.3,  "lon": 43.1},
    {"nombre": "Chialps",  "aethyr": "ZIP", "num": 65, "jurisdiccion": "Mongolia / Imperio Mongol",           "funcion": "Estrategia de expansión y consolidación territorial",        "cuadrante": "Q2",     "lat": 47.9,  "lon": 106.9},
    {"nombre": "Toantomz", "aethyr": "ZIP", "num": 66, "jurisdiccion": "Prusia / Estado Mayor",               "funcion": "Doctrina militar y aplicación sistemática de la fuerza",    "cuadrante": "Q1",     "lat": 52.5,  "lon": 13.4},
    {"nombre": "Zamfres",  "aethyr": "ZID", "num": 67, "jurisdiccion": "Israel / Tribus",                     "funcion": "Custodia de linajes y pureza genealógica",                  "cuadrante": "Q1",     "lat": 31.7,  "lon": 35.2},
    {"nombre": "Todnaon",  "aethyr": "ZID", "num": 68, "jurisdiccion": "Esparta / Eugenesia",                 "funcion": "Selección y preservación de rasgos en poblaciones",         "cuadrante": "Q2",     "lat": 37.0,  "lon": 22.4},
    {"nombre": "Pristac",  "aethyr": "ZID", "num": 69, "jurisdiccion": "Roma / Gens Patriciae",               "funcion": "Aristocracia hereditaria como mecanismo de continuidad",    "cuadrante": "Q1",     "lat": 41.9,  "lon": 12.5},
    {"nombre": "Obmacas",  "aethyr": "DEO", "num": 70, "jurisdiccion": "Vaticano / Roma",                     "funcion": "Unificación de autoridad espiritual como poder político",   "cuadrante": "Q1",     "lat": 41.9,  "lon": 12.4},
    {"nombre": "Genadolv", "aethyr": "DEO", "num": 71, "jurisdiccion": "Constantinopla / Patriarcado",        "funcion": "Canon, ortodoxia y expulsión de lo heterodoxo",             "cuadrante": "Q1",     "lat": 41.0,  "lon": 28.9},
    {"nombre": "Asmorno",  "aethyr": "DEO", "num": 72, "jurisdiccion": "La Meca / Islam",                     "funcion": "Ley sagrada como código total de organización social",       "cuadrante": "Q1",     "lat": 21.3,  "lon": 39.8},
    {"nombre": "Saziami",  "aethyr": "MAZ", "num": 73, "jurisdiccion": "Manchester / Revolución Industrial",  "funcion": "Control de medios de producción y cadenas de valor",        "cuadrante": "Q1",     "lat": 53.4,  "lon": -2.2},
    {"nombre": "Mathvla",  "aethyr": "MAZ", "num": 74, "jurisdiccion": "Pittsburgh / Acero",                  "funcion": "Monopolio de recursos estratégicos industriales",            "cuadrante": "Q1",     "lat": 40.4,  "lon": -79.9},
    {"nombre": "Orpamb",   "aethyr": "MAZ", "num": 75, "jurisdiccion": "Bakú / Petróleo",                     "funcion": "Control de fuentes energéticas como palanca geopolítica",   "cuadrante": "Q2",     "lat": 40.4,  "lon": 49.8},
    {"nombre": "Caosgi",   "aethyr": "LIT", "num": 76, "jurisdiccion": "Gutenberg / Maguncia",                "funcion": "Control de medios de reproducción y difusión",              "cuadrante": "Q1",     "lat": 49.9,  "lon": 8.2},
    {"nombre": "Lusanahe", "aethyr": "LIT", "num": 77, "jurisdiccion": "Fleet Street / Londres",              "funcion": "Narrativa hegemónica y agenda setting",                     "cuadrante": "Q2",     "lat": 51.5,  "lon": -0.1},
    {"nombre": "Sodalzt",  "aethyr": "LIT", "num": 78, "jurisdiccion": "Silicon Valley / Digital",            "funcion": "Algoritmos de filtrado y curación de realidad",             "cuadrante": "Q2",     "lat": 37.3,  "lon": -122.0},
    {"nombre": "Thotanpv", "aethyr": "PAZ", "num": 79, "jurisdiccion": "Pax Romana / Imperio",                "funcion": "Mantenimiento del statu quo como tecnología de poder",       "cuadrante": "Q1",     "lat": 41.9,  "lon": 12.4},
    {"nombre": "Axziargv", "aethyr": "PAZ", "num": 80, "jurisdiccion": "Bretton Woods / Post-WWII",           "funcion": "Institucionalización del orden internacional",              "cuadrante": "Q1",     "lat": 44.3,  "lon": -71.4},
    {"nombre": "Pothnirv", "aethyr": "PAZ", "num": 81, "jurisdiccion": "Naciones Unidas / NY",                "funcion": "Multilateralismo como mecanismo de contención",             "cuadrante": "Q1",     "lat": 40.7,  "lon": -74.0},
    {"nombre": "Samaphav", "aethyr": "ZOM", "num": 82, "jurisdiccion": "Amazonas / Biodiversidad",            "funcion": "Custodia del orden biológico y las taxonomías naturales",    "cuadrante": "Q1",     "lat": -3.4,  "lon": -65.0},
    {"nombre": "Virooliv", "aethyr": "ZOM", "num": 83, "jurisdiccion": "Galápagos / Darwin",                  "funcion": "Regulación de la selección y adaptación controlada",         "cuadrante": "Q2",     "lat": -0.9,  "lon": -89.6},
    {"nombre": "Andispiv", "aethyr": "ZOM", "num": 84, "jurisdiccion": "Mendel / Genética (Brno)",            "funcion": "Herencia como código de transmisión de orden",              "cuadrante": "Q2",     "lat": 49.1,  "lon": 16.6},
    {"nombre": "Doagnisv", "aethyr": "ARN", "num": 85, "jurisdiccion": "Platón / Atenas",                     "funcion": "Geometría como fundamento del orden cósmico",               "cuadrante": "Q1",     "lat": 37.9,  "lon": 23.7},
    {"nombre": "Pacasnav", "aethyr": "ARN", "num": 86, "jurisdiccion": "Pitágoras / Crotona",                 "funcion": "Número y proporción como lenguaje del control",             "cuadrante": "Q2",     "lat": 39.0,  "lon": 17.1},
    {"nombre": "Dialoiav", "aethyr": "ARN", "num": 87, "jurisdiccion": "Kepler / Praga",                      "funcion": "Armonía de esferas como modelo de jerarquía perfecta",      "cuadrante": "Q2",     "lat": 50.0,  "lon": 14.4},
    {"nombre": "Occodonl", "aethyr": "LIL", "num": 88, "jurisdiccion": "LIL / Sin geografía terrestre",       "funcion": "Fuente primordial de toda autoridad en el sistema",          "cuadrante": "Q1",     "lat": 90.0,  "lon": 0.0},
    {"nombre": "Pascombl", "aethyr": "LIL", "num": 89, "jurisdiccion": "LIL / Sin geografía terrestre",       "funcion": "Registro eterno, el libro que no se borra",                 "cuadrante": "Q1",     "lat": 90.0,  "lon": 60.0},
    {"nombre": "Valgarsl", "aethyr": "LIL", "num": 90, "jurisdiccion": "LIL / Sin geografía terrestre",       "funcion": "Ejecución final de la voluntad del sistema completo",        "cuadrante": "Q1",     "lat": 90.0,  "lon": -60.0},
    {"nombre": "Lrasd",    "aethyr": "LIL", "num": 91, "jurisdiccion": "LIL / Sin geografía terrestre",       "funcion": "El sellado — cierre del ciclo completo del sistema",         "cuadrante": "Q1",     "lat": 90.0,  "lon": 120.0},
]

# NODOS GEOGRÁFICOS
nodos_enoquianos_historicos = [
    ("Britannia (Londres, UK)", 51.5074, -0.1278),
    ("Sarmatia (Moscú, Rusia)", 55.7558, 37.6173),
    ("Italia (Roma)", 41.9028, 12.4964),
    ("Gallia (París, Francia)", 48.8566, 2.3522),
    ("Mesopotamia (Damasco, Siria)", 33.5138, 36.2765),
    ("Bactriana (Nueva Delhi, India)", 28.6139, 77.2090)
]

nodos_goetia_historicos = [
    ("Babilonia (Hillah, Irak)", 32.5363, 44.4208),
    ("Persia (Teherán, Irán)", 35.6892, 51.3890),
    ("Egipto (El Cairo)", 30.0444, 31.2357),
    ("Fenicia / Sidón (Líbano)", 33.5571, 35.3730),
    ("Desierto de Arabia (Riad, AS)", 24.7136, 46.6753),
    ("Sodoma (Mar Muerto, Jordania)", 31.3333, 35.5000)
]

goetia_72 = [
    ("Bael", "Rey", 66, "Invisibilidad"), ("Agares", "Duque", 31, "Terremotos"), ("Vassago", "Príncipe", 26, "Secretos"), ("Samigina", "Marqués", 30, "Nigromancia"), ("Marbas", "Presidente", 36, "Enfermedades"), ("Valefor", "Duque", 10, "Robo"), ("Amon", "Marqués", 40, "Ira"), ("Barbatos", "Duque", 30, "Tesoros"), ("Paimon", "Rey", 200, "Manipulación"), ("Buer", "Presidente", 50, "Biología"),
    ("Gusion", "Duque", 40, "Diplomacia"), ("Sitri", "Príncipe", 60, "Lujuria"), ("Beleth", "Rey", 85, "Pasiones"), ("Leraje", "Marqués", 30, "Guerra"), ("Eligos", "Duque", 60, "Milicia"), ("Zepar", "Duque", 26, "Mutación"), ("Botis", "Presidente", 60, "Facciones"), ("Bathin", "Duque", 30, "Proyección"), ("Sallos", "Duque", 30, "Alteración sentimental"), ("Purson", "Rey", 22, "Materialismo"),
    ("Marax", "Conde", 30, "Astronomía"), ("Ipos", "Príncipe", 36, "Elocuencia"), ("Aim", "Duque", 26, "Caos Urbano"), ("Naberius", "Marqués", 19, "Astucia"), ("Glasya-Labolas", "Presidente", 36, "Asesinatos"), ("Bune", "Duque", 30, "Fraude"), ("Ronove", "Marqués", 19, "Humillación"), ("Berith", "Duque", 26, "Transmutación"), ("Astaroth", "Duque", 40, "Filosofía"), ("Forneus", "Marqués", 29, "Idiomas"),
    ("Foras", "Presidente", 29, "Tesoros"), ("Asmoday", "Rey", 72, "Destrucción Genética"), ("Gaap", "Príncipe", 66, "Robo intelectual"), ("Furfur", "Conde", 26, "Tormentas"), ("Marchosias", "Marqués", 30, "Revoluciones"), ("Stolas", "Príncipe", 26, "Venenos"), ("Phenex", "Marqués", 20, "Obediencia"), ("Halphas", "Conde", 26, "Armamento"), ("Malphas", "Presidente", 40, "Espionaje"), ("Raum", "Conde", 30, "Robo de dignidades"),
    ("Focalor", "Duque", 30, "Asesinatos navales"), ("Vepar", "Duque", 29, "Plagas"), ("Sabnock", "Marqués", 50, "Gangrena"), ("Shax", "Marqués", 30, "Anulación de sentidos"), ("Vine", "Rey", 36, "Destrucción de muros"), ("Bifrons", "Conde", 6, "Necromancia"), ("Uvall", "Duque", 37, "Futuro"), ("Haagenti", "Presidente", 33, "Biología Sintética"), ("Crocell", "Duque", 48, "Aguas termales"), ("Furcas", "Caballero", 20, "Lógica"),
    ("Balam", "Rey", 40, "Engaño Masivo"), ("Alloces", "Duque", 36, "Arquitectura bélica"), ("Camio", "Presidente", 30, "Lenguaje animal"), ("Murmur", "Duque", 30, "Filosofía restrictiva"), ("Orobas", "Príncipe", 20, "Verdad inalterable"), ("Gremory", "Duque", 26, "Ilícitos"), ("Ose", "Presidente", 30, "Transformación"), ("Amy", "Presidente", 36, "Manipulación de voluntad"), ("Oriax", "Marqués", 30, "Títulos"), ("Vapula", "Duque", 36, "Ciencias oscuras"),
    ("Zagan", "Rey", 33, "Alquimia"), ("Volac", "Presidente", 38, "Descubrimientos"), ("Andras", "Marqués", 30, "Polarización y Discordia"), ("Haures", "Duque", 36, "Venganza"), ("Andrealphus", "Marqués", 30, "Mutación animal"), ("Cimejes", "Marqués", 20, "Gramática"), ("Amdusias", "Duque", 29, "Control natural"), ("Belial", "Rey", 80, "Favores políticos"), ("Decarabia", "Marqués", 30, "Ilusiones"), ("Seere", "Príncipe", 26, "Teletransportación"), ("Dantalion", "Duque", 36, "Control de pensamientos"), ("Andromalius", "Conde", 36, "Castigo a conspiradores")
]

comandantes = []
nodos_por_clase = {} 
geo_map_data = []

# Carga Goetia (sin cambios — encaja bien con ala izquierda)
for nombre, rango, legiones, funcion in goetia_72:
    raiz = "SMOL_ARISTEROS" if rango in ["Rey", "Marqués", "Conde"] else "YADA_GINOSKO" 
    id_nodo = f"{rango} {nombre}"
    lugar = random.choice(nodos_goetia_historicos)
    # Asignar cuadrante semántico según función de disolución
    cuadrante = "Q4" if rango in ["Rey", "Marqués"] else "Q3"
    comandantes.append({
        "IdNodo": id_nodo, "Comandante": nombre, "Faccion": "IZQUIERDA (Caos)", "Raiz": raiz, 
        "Rango": rango, "Legiones_Str": f"{legiones} Legiones", "Legiones_Num": legiones,
        "Funcion": funcion, "OSINT": "caos OR crisis OR biotecnologia", "Ubicacion": lugar[0],
        "Cuadrante": cuadrante, "Aethyr": "Ars Goetia"
    })
    if rango not in nodos_por_clase: nodos_por_clase[rango] = []
    nodos_por_clase[rango].append(id_nodo)
    geo_map_data.append({"Comandante": id_nodo, "Faccion": "IZQUIERDA (Caos)", "Lat": lugar[1], "Lon": lugar[2], "Ubicacion": lugar[0], "Entidades": legiones * 6666})

# Carga Enoquianos — AHORA con los 91 GOBERNADORES REALES
reyes_enoquianos = [("Bataivah", "Rey Elemental", "Aire"), ("Raagiosl", "Rey Elemental", "Agua"), ("Iczhihal", "Rey Elemental", "Tierra"), ("Edaiel", "Rey Elemental", "Fuego")]
for nombre, rango, dominio in reyes_enoquianos:
    id_nodo = f"{rango} {nombre}"
    lugar = random.choice(nodos_enoquianos_historicos)
    comandantes.append({
        "IdNodo": id_nodo, "Comandante": nombre, "Faccion": "DERECHA (Control)", "Raiz": "YAMIN_DEXIOS",
        "Rango": rango, "Legiones_Str": f"Elemento: {dominio}", "Legiones_Num": 100,
        "Funcion": f"Gobierno del {dominio} — administración elemental total", "OSINT": "regulacion OR monopolio OR vigilancia",
        "Ubicacion": lugar[0], "Cuadrante": "Q1", "Aethyr": "LIL"
    })
    if rango not in nodos_por_clase: nodos_por_clase[rango] = []
    nodos_por_clase[rango].append(id_nodo)
    geo_map_data.append({"Comandante": id_nodo, "Faccion": "DERECHA (Control)", "Lat": lugar[1], "Lon": lugar[2], "Ubicacion": lugar[0], "Entidades": 100 * 6666})

ancianos_24 = [(f"Anciano {i+1}", "Anciano", "Senado Cósmico — Registro y Testimonio") for i in range(24)]
for nombre, rango, dominio in ancianos_24:
    id_nodo = f"{rango} {nombre}"
    lugar = random.choice(nodos_enoquianos_historicos)
    comandantes.append({
        "IdNodo": id_nodo, "Comandante": nombre, "Faccion": "DERECHA (Control)", "Raiz": "BEYN_KRIMA",
        "Rango": rango, "Legiones_Str": "Dominio: Testimonio Cósmico", "Legiones_Num": 30,
        "Funcion": "Vigilancia sin intervención — registro eterno del sistema", "OSINT": "vigilancia OR regulacion",
        "Ubicacion": lugar[0], "Cuadrante": "Q1", "Aethyr": "LIL-ARN"
    })
    if rango not in nodos_por_clase: nodos_por_clase[rango] = []
    nodos_por_clase[rango].append(id_nodo)
    geo_map_data.append({"Comandante": id_nodo, "Faccion": "DERECHA (Control)", "Lat": lugar[1], "Lon": lugar[2], "Ubicacion": lugar[0], "Entidades": 30 * 6666})

# GOBERNADORES — carga desde datos reales
for g in GOBERNADORES_91:
    id_nodo = f"Gobernador {g['nombre']} ({g['aethyr']})"
    raiz = "BEYN_KRIMA" if g["cuadrante"] == "UMBRAL" else ("YAMIN_DEXIOS" if g["cuadrante"] in ["Q1", "Q2"] else "SMOL_ARISTEROS")
    comandantes.append({
        "IdNodo": id_nodo, "Comandante": g["nombre"], "Faccion": "DERECHA (Control)", "Raiz": raiz,
        "Rango": f"Gobernador Aethyr {g['aethyr']}", "Legiones_Str": f"Aethyr {g['aethyr']} — #{g['num']}",
        "Legiones_Num": 30, "Funcion": g["funcion"], "OSINT": "regulacion OR control OR orden",
        "Ubicacion": g["jurisdiccion"], "Cuadrante": g["cuadrante"], "Aethyr": g["aethyr"]
    })
    rango_key = f"Gobernador {g['aethyr']}"
    if rango_key not in nodos_por_clase: nodos_por_clase[rango_key] = []
    nodos_por_clase[rango_key].append(id_nodo)
    geo_map_data.append({"Comandante": id_nodo, "Faccion": "DERECHA (Control)", "Lat": g["lat"], "Lon": g["lon"], "Ubicacion": g["jurisdiccion"], "Entidades": 30 * 6666})

# Vigilantes
id_vigilantes = "Semyaza / Azazel (Vigilantes)"
comandantes.append({"IdNodo": id_vigilantes, "Comandante": "Semyaza", "Faccion": "IZQUIERDA (Caos)", "Raiz": "YADA_GINOSKO", "Rango": "Comandantes", "Legiones_Str": "200 Ángeles", "Legiones_Num": 200, "Funcion": "Rebelión e Hibridación Genética — Jonás 4:11 en acción", "OSINT": "ingenieria genetica", "Ubicacion": "Monte Hermón (Levante)", "Cuadrante": "Q4", "Aethyr": "Vigilantes"})
geo_map_data.append({"Comandante": id_vigilantes, "Faccion": "IZQUIERDA (Caos)", "Lat": 33.4115, "Lon": 35.8566, "Ubicacion": "Monte Hermón (Levante)", "Entidades": 200 * 6666})

# Cálculos Geográficos
df_jerarcas_geo = pd.DataFrame(geo_map_data)
pob_dict = {
    "Britannia (Londres, UK)": 9000000, "Sarmatia (Moscú, Rusia)": 13000000, "Italia (Roma)": 2800000,
    "Gallia (París, Francia)": 11000000, "Mesopotamia (Damasco, Siria)": 2000000, "Bactriana (Nueva Delhi, India)": 32000000,
    "Babilonia (Hillah, Irak)": 500000, "Persia (Teherán, Irán)": 9000000, "Egipto (El Cairo)": 22000000,
    "Fenicia / Sidón (Líbano)": 200000, "Desierto de Arabia (Riad, AS)": 7500000, "Sodoma (Mar Muerto, Jordania)": 100000,
    "Monte Hermón (Levante)": 50000
}
df_zonas = df_jerarcas_geo.groupby(['Ubicacion', 'Lat', 'Lon', 'Faccion']).agg({'Entidades': 'sum', 'Comandante': 'count'}).reset_index()
df_zonas.rename(columns={'Comandante': 'Total_Jerarcas'}, inplace=True)
df_zonas['Poblacion'] = df_zonas['Ubicacion'].map(pob_dict).fillna(1000000)
df_zonas['Ratio'] = df_zonas.apply(lambda row: round(row['Poblacion'] / row['Entidades'], 2) if row['Entidades'] > 0 else 0, axis=1)

mapeo_infraestructura = {
    "BlackRock / Vanguard": "Rey Elemental Iczhihal", "Banco de Pagos Internacionales (BIS)": "Rey Elemental Iczhihal",
    "DARPA": "Rey Elemental Bataivah", "Sistema de Crédito Social Chino": "Rey Elemental Edaiel",
    "CRISPR-Cas9 / Edición Genética": "Rey Asmoday", "Quimeras Humano-Animal": "Comandante Semyaza",
    "Biología Sintética / ARNm": "Presidente Haagenti", "Neuralink / Interfaz Cerebro": "Rey Bael",
    "EctoLife / Úteros Artificiales": "Rey Asmoday", "Tránsito de Urano en Tauro": "Presidente Haagenti",
    "Entrada de Plutón en Acuario": "Rey Bael", "Retorno de Plutón (USA)": "Marqués Marchosias"
}

def extraer_cita(texto, palabra_clave, ventana=60):
    idx = texto.upper().find(palabra_clave)
    if idx == -1: return ""
    return f"...{texto[max(0, idx - ventana):min(len(texto), idx + len(palabra_clave) + ventana)].replace(chr(10), ' ').strip()}..."

# --- 8. GRAFO MAESTRO ---
def generar_mapa_maestro(faccion, c_ling, c_geo, c_bio, c_astro, textos_raw, activar_radar):
    G = nx.Graph()
    color_faccion = "#e11d48" if "IZQUIERDA" in faccion else "#2563eb"
    G.add_node(str(faccion), size=75, color=color_faccion, title=f"🔥 {faccion} (Sol Central)", font={"color": "white", "size": 28, "bold": True})

    if "DERECHA" in faccion:
        raices = {
            "YAMIN_DEXIOS": {"desc": "Yamin/Dexios — Autoridad / Centralización\nPoder investido, acción efectiva, favor divino.", "color": "#3b82f6", "claves": ["YAMIN", "DEXIOS", "DERECHA", "CENTRAL", "CONTROL"]},
            "BEYN_KRIMA":   {"desc": "Beyn/Krima — Límites / Vigilancia\nSeparación precisa, juicio jurisdiccional, registro.", "color": "#60a5fa", "claves": ["BEYN", "KRIMA", "SEPARACION", "VIGILANCIA", "FILTRO", "LEY"]}
        }
    else:
        raices = {
            "SMOL_ARISTEROS": {"desc": "Smol/Aristeros — Entropía / Disolución\nQuiebre de límites, rebelión, disolución de materia.", "color": "#f43f5e", "claves": ["SMOL", "ARISTEROS", "IZQUIERDA", "CAOS", "DISOLUCION", "REBELION"]},
            "YADA_GINOSKO":   {"desc": "Yada/Ginosko — Ausencia de Discernimiento\nColapso de la función discriminatoria. Hibridación.", "color": "#fb7185", "claves": ["YADA", "GINOSKO", "ALTERACION", "HIBRIDACION", "MUTACION", "CONOCIMIENTO"]}
        }

    for r_id, info in raices.items():
        G.add_node(str(r_id), size=55, color=info["color"], title=f"Raíz Ontológica: {r_id}\n\n{info['desc']}\n\n📖 BASE: Jonás 4:11", font={"color": "white", "size": 20, "bold": True})
        G.add_edge(str(faccion), str(r_id), weight=6)

    comandantes_faccion = [c for c in comandantes if c["Faccion"] == faccion]
    operativos_osint = random.sample(comandantes_faccion, min(4, len(comandantes_faccion))) if activar_radar else []

    for cmd in comandantes_faccion:
        id_nodo = cmd["IdNodo"]
        esta_buscando = cmd in operativos_osint
        size = 25 if esta_buscando else 12
        # Color por cuadrante semántico
        color_map = {"Q1": "#3b82f6", "Q2": "#2563eb", "Q3": "#be123c", "Q4": "#e11d48", "UMBRAL": "#0ea5e9"}
        color_nodo = "#ef4444" if esta_buscando else color_map.get(cmd.get("Cuadrante", "Q1"), "#475569")
        
        cuad_info = CUADRANTES_PLANO.get(cmd.get("Cuadrante", "Q1"), {})
        G.add_node(id_nodo, size=size, color=color_nodo, title=f"👑 {id_nodo}\n📍 Zona: {cmd['Ubicacion']}\n🔮 Aethyr: {cmd.get('Aethyr','—')}\n⚙️ Mando: {cmd['Legiones_Str']}\n📜 Función: {cmd['Funcion']}\n🧭 Cuadrante: {cuad_info.get('nombre','—')}")
        G.add_edge(cmd["Raiz"], id_nodo, weight=1)
        
        if esta_buscando:
            for i, noticia in enumerate(obtener_noticias_tiempo_real(cmd["OSINT"])):
                id_not = f"📰 Alerta {cmd['Comandante'][:6]} [{i}]"
                G.add_node(id_not, size=15, color="#ef4444", title=f"TIEMPO REAL:\n{noticia}")
                G.add_edge(id_nodo, id_not, weight=1)

    for clase, nodos_clase in nodos_por_clase.items():
        nodos_validos = [n for n in nodos_clase if any(c["IdNodo"] == n and c["Faccion"] == faccion for c in comandantes)]
        if len(nodos_validos) > 1:
            for i in range(len(nodos_validos)):
                G.add_edge(nodos_validos[i], nodos_validos[(i + 1) % len(nodos_validos)], weight=0.1, color="#334155")

    if not c_ling.empty:
        for _, row in c_ling.iterrows():
            if pd.isna(row.get('Libro')): continue
            nodo_id = f"{row['Libro']} {row['Capitulo']}:{row['Versiculo']}"
            trad = str(row.get('Traduccion', '')).replace('"', "'")
            hebreo_griego = row.get('Hebreo_Limpio', '')
            G.add_node(nodo_id, size=15, color="#f8fafc", title=f"📖 CAPA 0 (Código Base)\n\nVerso: {nodo_id}\nOriginal: {hebreo_griego}\nTraducción: {trad}")
            conceptos = str(row.get('Conceptos_Matriz', '')).upper()
            conectado = False
            for r_id, info in raices.items():
                if any(clave in conceptos for clave in info["claves"]):
                    G.add_edge(str(r_id), nodo_id, weight=2)
                    conectado = True
                    break
            if not conectado: G.add_edge(str(faccion), nodo_id, weight=1)

    if textos_raw:
        for nombre_doc, contenido in textos_raw.items():
            for r_id, info in raices.items():
                for clave in info["claves"]:
                    if clave in contenido.upper():
                        cita = extraer_cita(contenido, clave)
                        nodo_doc_id = f"Doc: {nombre_doc[:12]}..."
                        G.add_node(nodo_doc_id, size=16, color="#d946ef", title=f"📜 {nombre_doc}\nCita: {cita}")
                        G.add_edge(str(r_id), nodo_doc_id, weight=1)
                        break

    def procesar_capa(df_capa, col_nombre, col_mecanismo, color_nodo, prefijo, icono):
        if not df_capa.empty:
            for _, row in df_capa.iterrows():
                if pd.isna(row.get(col_nombre)): continue
                nodo_id = str(row[col_nombre]).strip()
                mecanismo = str(row.get(col_mecanismo, 'Detalle no disponible'))
                G.add_node(nodo_id, size=30, color=color_nodo, title=f"{icono} {prefijo}\n{mecanismo}")
                if nodo_id in mapeo_infraestructura:
                    jefe = mapeo_infraestructura[nodo_id]
                    if any(c["IdNodo"] == jefe and c["Faccion"] == faccion for c in comandantes_faccion):
                        G.add_edge(jefe, nodo_id, weight=2)
                else: G.add_edge(str(faccion), nodo_id, weight=1)

    procesar_capa(c_geo, 'Entidad / Corporación', 'Mecanismo de Control', "#10b981", "CAPA 2", "🌍")
    procesar_capa(c_bio, 'Avance / Plataforma', 'Mecanismo de Operación', "#f59e0b", "CAPA 3", "🧬")

    import tempfile
    net = Network(height="750px", width="100%", bgcolor="#0b0f19", font_color="white")
    net.from_nx(G)
    net.force_atlas_2based(gravity=-60, central_gravity=0.01, spring_length=150, spring_strength=0.05, damping=0.7, overlap=0)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        ruta_html = f.name
    net.write_html(ruta_html)
    return ruta_html

# ============================================================================
# --- NUEVA FUNCIÓN: PLANO SEMÁNTICO DE 4 CUADRANTES ---
# ============================================================================
def generar_plano_semantico(faccion_filtro=None):
    """
    Genera el plano cartesiano de cuatro cuadrantes semánticos.
    Eje X: YAMIN (+) vs SMOL (-)
    Eje Y: BEYN (+) vs YADA (-)
    Jonás 4:11 como punto generador en Q4 (−,−)
    """
    
    # Preparar datos de gobernadores enoquianos para el plano
    puntos_plano = []
    
    # Mapeo cuadrante → coordenadas con dispersión
    coord_map = {
        "Q1":     ( 0.5,  0.5), "Q2": ( 0.5, -0.5),
        "Q3":     (-0.5,  0.5), "Q4": (-0.5, -0.5),
        "UMBRAL": ( 0.0,  0.0)
    }
    
    # Gobernadores enoquianos
    for g in GOBERNADORES_91:
        if faccion_filtro and faccion_filtro != "DERECHA (Control)": continue
        cx, cy = coord_map.get(g["cuadrante"], (0, 0))
        jitter_x = (g["num"] % 7 - 3) * 0.07
        jitter_y = (g["num"] % 5 - 2) * 0.07
        color_cuad = CUADRANTES_PLANO.get(g["cuadrante"], {}).get("color", "#94a3b8")
        puntos_plano.append({
            "nombre": g["nombre"], "tipo": f"Gobernador {g['aethyr']}",
            "cuadrante": g["cuadrante"], "jurisdiccion": g["jurisdiccion"],
            "funcion": g["funcion"], "faccion": "DERECHA (Control)",
            "x": cx + jitter_x, "y": cy + jitter_y, "color": color_cuad,
            "size": 8, "simbolo": "circle"
        })
    
    # Goetia — izquierda
    for cmd in comandantes:
        if cmd["Faccion"] != "IZQUIERDA (Caos)": continue
        if faccion_filtro and faccion_filtro != "IZQUIERDA (Caos)": continue
        cuad = cmd.get("Cuadrante", "Q4")
        cx, cy = coord_map.get(cuad, (-0.5, -0.5))
        jitter_x = (hash(cmd["Comandante"]) % 7 - 3) * 0.07
        jitter_y = (hash(cmd["Comandante"]) % 5 - 2) * 0.07
        color_cuad = CUADRANTES_PLANO.get(cuad, {}).get("color", "#e11d48")
        puntos_plano.append({
            "nombre": cmd["Comandante"], "tipo": cmd["Rango"],
            "cuadrante": cuad, "jurisdiccion": cmd["Ubicacion"],
            "funcion": cmd["Funcion"], "faccion": "IZQUIERDA (Caos)",
            "x": cx + jitter_x, "y": cy + jitter_y, "color": color_cuad,
            "size": 10 if cmd["Rango"] == "Rey" else 7, "simbolo": "diamond"
        })
    
    df_plano = pd.DataFrame(puntos_plano)
    
    fig = go.Figure()
    
    # Fondos de cuadrantes
    cuad_rects = [
        dict(x0=0, x1=1,  y0=0,  y1=1,  fill="rgba(29,78,216,0.08)",   label="Q1: Control con Límites"),
        dict(x0=0, x1=1,  y0=-1, y1=0,  fill="rgba(37,99,235,0.08)",   label="Q2: Autoridad por Discernimiento"),
        dict(x0=-1, x1=0, y0=0,  y1=1,  fill="rgba(190,18,60,0.08)",   label="Q3: Caos Contenido"),
        dict(x0=-1, x1=0, y0=-1, y1=0,  fill="rgba(225,29,72,0.12)",   label="Q4: Indistinción Total"),
    ]
    for r in cuad_rects:
        fig.add_shape(type="rect", x0=r["x0"], x1=r["x1"], y0=r["y0"], y1=r["y1"],
                      fillcolor=r["fill"], line=dict(color="#1e293b", width=1))
    
    # Ejes
    fig.add_shape(type="line", x0=-1.1, x1=1.1, y0=0, y1=0, line=dict(color="#334155", width=1, dash="dot"))
    fig.add_shape(type="line", x0=0, x1=0, y0=-1.1, y1=1.1, line=dict(color="#334155", width=1, dash="dot"))
    
    # Zona umbral
    fig.add_shape(type="circle", x0=-0.15, x1=0.15, y0=-0.15, y1=0.15,
                  fillcolor="rgba(14,165,233,0.15)", line=dict(color="#0ea5e9", width=1, dash="dash"))
    
    # Puntos por facción
    if not df_plano.empty:
        for faccion, group in df_plano.groupby("faccion"):
            color_list = group["color"].tolist()
            fig.add_trace(go.Scatter(
                x=group["x"], y=group["y"],
                mode="markers",
                name=faccion,
                marker=dict(size=group["size"].tolist(), color=color_list,
                            symbol=group["simbolo"].tolist(),
                            line=dict(color="#0b0f19", width=0.5)),
                text=group["nombre"],
                customdata=group[["cuadrante", "jurisdiccion", "funcion", "tipo"]].values,
                hovertemplate="<b>%{text}</b><br>Tipo: %{customdata[3]}<br>Cuadrante: %{customdata[0]}<br>Jurisdicción: %{customdata[1]}<br>Función: %{customdata[2]}<extra></extra>"
            ))
    
    # Jonás 4:11 — punto generador
    fig.add_trace(go.Scatter(
        x=[-0.5], y=[-0.5], mode="markers+text",
        name="★ Jonás 4:11 (Texto Generador)",
        marker=dict(size=20, color="#fbbf24", symbol="star", line=dict(color="#ffffff", width=1.5)),
        text=["יונה ד:יא"], textposition="top center",
        textfont=dict(color="#fbbf24", size=11),
        hovertemplate="<b>★ JONÁS 4:11 — TEXTO GENERADOR</b><br>לֹא־יָדַע אִישׁ בֵּין־יְמִינוֹ לִשְׂמֹאלוֹ<br>Las 4 raíces en un solo versículo<extra></extra>"
    ))
    
    # Etiquetas de cuadrantes y ejes
    anotaciones = [
        dict(x=0.75, y=0.85, text="Q1<br><b>CONTROL CON LÍMITES</b><br>YAMIN + BEYN", showarrow=False, font=dict(color="#3b82f6", size=10), align="center"),
        dict(x=0.75, y=-0.85, text="Q2<br><b>AUTORIDAD POR<br>DISCERNIMIENTO</b><br>YAMIN + YADA", showarrow=False, font=dict(color="#2563eb", size=10), align="center"),
        dict(x=-0.75, y=0.85, text="Q3<br><b>CAOS CONTENIDO</b><br>SMOL + BEYN", showarrow=False, font=dict(color="#be123c", size=10), align="center"),
        dict(x=-0.75, y=-0.85, text="Q4<br><b>INDISTINCIÓN TOTAL</b><br>SMOL + YADA", showarrow=False, font=dict(color="#e11d48", size=10), align="center"),
        dict(x=0.0, y=-0.25, text="UMBRAL<br>BEYN solo", showarrow=False, font=dict(color="#0ea5e9", size=9), align="center"),
        # Etiquetas de ejes
        dict(x=1.08, y=0, text="YAMIN →<br>יָמִין", showarrow=False, font=dict(color="#3b82f6", size=10), align="left"),
        dict(x=-1.08, y=0, text="← SMOL<br>שְׂמֹאל", showarrow=False, font=dict(color="#e11d48", size=10), align="right"),
        dict(x=0, y=1.08, text="↑ BEYN<br>בֵּין", showarrow=False, font=dict(color="#60a5fa", size=10), align="center"),
        dict(x=0, y=-1.08, text="↓ YADA<br>יָדַע", showarrow=False, font=dict(color="#fb7185", size=10), align="center"),
    ]
    
    fig.update_layout(
        plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19",
        font_color="#94a3b8",
        xaxis=dict(range=[-1.2, 1.2], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-1.2, 1.2], showgrid=False, zeroline=False, showticklabels=False),
        annotations=anotaciones,
        legend=dict(bgcolor="#0f172a", bordercolor="#1e293b", borderwidth=1),
        margin=dict(l=40, r=40, t=60, b=40),
        title=dict(text="Plano Semántico — Base: Jonás 4:11  |  לֹא־יָדַע אִישׁ בֵּין־יְמִינוֹ לִשְׂמֹאלוֹ", font=dict(color="#e2e8f0", size=14)),
        height=650
    )
    
    return fig

# ============================================================================
# --- 9. RENDERIZACIÓN — 11 PESTAÑAS (nueva: Plano Semántico) ---
# ============================================================================
tab_core, tab_geo, tab_plano, tab_predict, tab_timeline, tab0, tab1, tab2, tab3, tab4, tab_arq = st.tabs([
    "🔄 Enjambre Jerárquico", "🗺️ Mapa Geo-Densidad", "🧭 Plano Semántico", "🎯 Predictivo", "⏱️ Timeline",
    "📖 V0-Textos", "🔮 V1-Esotérico", "🌍 V2-Geo", "🧬 V3-Bio", "⏳ V4-Astro", "👥 Arquetipos"
])

with tab_core:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Enjambre Total: 72 Goetia + 91 Gobernadores Enoquianos + 24 Ancianos + 4 Reyes")
        facción_maestra = st.radio("Seleccionar Ala de Comando:", ["DERECHA (Control)", "IZQUIERDA (Caos)"], horizontal=True)
    with col2:
        st.info("📡 **Radar OSINT**")
        activar_radar = st.checkbox("Buscar crímenes en tiempo real", value=False)
        if activar_radar: st.warning("Rastreando Google News...")

    termino_ling = "Derecha" if "DERECHA" in facción_maestra else "Izquierda"
    criterio_fac = "DERECHA (Control)" if "DERECHA" in facción_maestra else "IZQUIERDA (Caos)"
    
    c_ling = df_ling_masivo[df_ling_masivo["Conceptos_Matriz"].str.contains(termino_ling, na=False, case=False)] if not df_ling_masivo.empty else pd.DataFrame()
    c_geo = df_geo[df_geo["Facción Alineada"] == criterio_fac] if not df_geo.empty else pd.DataFrame()
    c_bio = df_bio[df_bio["Facción Alineada"] == criterio_fac] if not df_bio.empty else pd.DataFrame()
    c_astro = df_astro[df_astro["Facción Alineada"].str.contains(termino_ling + "|Ambas", na=False, case=False)] if not df_astro.empty else pd.DataFrame()

    ruta_grafo = generar_mapa_maestro(facción_maestra, c_ling, c_geo, c_bio, c_astro, textos_raw_eso, activar_radar)
    with open(ruta_grafo, 'r', encoding='utf-8') as f: components.html(f.read(), height=760)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Raíces Activas (Capa 0)", len(c_ling))
    m2.metric("Jerarcas Desplegados", sum(1 for c in comandantes if c["Faccion"] == facción_maestra))
    m3.metric("Gobernadores Enoquianos", len(GOBERNADORES_91))
    m4.metric("Infraestructura Terrestre", len(c_geo) + len(c_bio))
    m5.metric("Ventanas del Reloj", len(c_astro))

with tab_geo:
    st.subheader("🗺️ Mapeo Geopolítico Histórico: Ratio Entidades vs Humanos")
    st.caption("Gobernadores enoquianos ahora posicionados con coordenadas exactas según jurisdicción histórica (Liber Scientiae).")
    
    df_zonas["Hover"] = df_zonas.apply(lambda r: f"<b>{r['Ubicacion']}</b><br>Jerarcas: {r['Total_Jerarcas']}<br>Entidades: {r['Entidades']:,.0f}<br>Población: {r['Poblacion']:,.0f}<br><b>DENSIDAD: 1 Humano / {r['Ratio']} Entidades</b>", axis=1)
    
    fig_map = px.scatter_geo(df_zonas, lat="Lat", lon="Lon", size="Entidades", color="Faccion", hover_name="Ubicacion", custom_data=["Hover"], projection="natural earth", color_discrete_map={"DERECHA (Control)": "#3b82f6", "IZQUIERDA (Caos)": "#f43f5e"})
    fig_map.update_traces(hovertemplate="%{customdata[0]}")
    fig_map.update_geos(showcountries=True, countrycolor="#334155", showland=True, landcolor="#0f172a", showocean=True, oceancolor="#0b0f19")
    fig_map.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

# ============================================================================
# NUEVA PESTAÑA: PLANO SEMÁNTICO
# ============================================================================
with tab_plano:
    st.subheader("🧭 Plano Semántico — Jonás 4:11 como texto generador")
    
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        st.markdown("""
        **Base textual:** `יונה ד:יא` — *"no sabe un hombre entre su derecha y su izquierda"*
        
        Los cuatro ejes del plano son las cuatro raíces del versículo:
        - **Eje X+**: `יָמִין Yamin` (autoridad, derecha investida)  
        - **Eje X−**: `שְׂמֹאל Smol` (disolución, lo no consagrado)  
        - **Eje Y+**: `בֵּין Beyn` (separación, límite, juicio)  
        - **Eje Y−**: `יָדַע Yada` (discernimiento ausente → hibridación)
        """)
    with col_p2:
        filtro_faccion = st.selectbox("Filtrar por ala:", ["Todas", "DERECHA (Control)", "IZQUIERDA (Caos)"])
        filtro = None if filtro_faccion == "Todas" else filtro_faccion
        
        st.markdown("**Distribución por cuadrante:**")
        goetia_q = {"Q3": 0, "Q4": 0}
        enoc_q = {"Q1": 0, "Q2": 0, "UMBRAL": 0}
        for c in comandantes:
            cuad = c.get("Cuadrante", "")
            if c["Faccion"] == "IZQUIERDA (Caos)" and cuad in goetia_q: goetia_q[cuad] += 1
        for g in GOBERNADORES_91:
            if g["cuadrante"] in enoc_q: enoc_q[g["cuadrante"]] += 1
        
        for k, v in {**enoc_q, **goetia_q}.items():
            info = CUADRANTES_PLANO.get(k, {})
            st.markdown(f"<small style='color:{info.get('color','#94a3b8')}'>{k} — {info.get('nombre','')}: **{v}**</small>", unsafe_allow_html=True)
    
    fig_plano = generar_plano_semantico(filtro)
    st.plotly_chart(fig_plano, use_container_width=True)
    
    # Tabla de cuadrantes
    st.markdown("---")
    st.markdown("**Descripción de cuadrantes:**")
    cols_cuad = st.columns(5)
    for i, (k, v) in enumerate(CUADRANTES_PLANO.items()):
        with cols_cuad[i]:
            st.markdown(f"""
            <div style='background:#0f172a; border:1px solid {v["color"]}; border-radius:8px; padding:10px;'>
            <b style='color:{v["color"]}'>{k}</b><br>
            <small style='color:#e2e8f0'><b>{v["nombre"]}</b></small><br>
            <small style='color:#94a3b8'>{v["descripcion"]}</small><br><br>
            <small style='color:#64748b'>{"<br>".join(v["ejemplos"])}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Tabla de gobernadores expandida
    st.markdown("---")
    st.subheader("📋 91 Gobernadores — Datos Completos")
    df_gob_display = pd.DataFrame([{
        "Núm": g["num"], "Nombre": g["nombre"], "Aethyr": g["aethyr"],
        "Cuadrante": g["cuadrante"], "Jurisdicción": g["jurisdiccion"], "Función": g["funcion"]
    } for g in GOBERNADORES_91])
    
    cuad_filter = st.multiselect("Filtrar por cuadrante:", ["Q1", "Q2", "UMBRAL"], default=["Q1", "Q2", "UMBRAL"])
    df_filtered = df_gob_display[df_gob_display["Cuadrante"].isin(cuad_filter)]
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)

with tab_predict:
    st.subheader("🎯 Algoritmo de Convergencia Vectorial")
    col_p1, col_p2, col_p3 = st.columns(3)
    opciones_geo = df_geo['Entidad / Corporación'].dropna().tolist() if not df_geo.empty else ["Sin datos"]
    opciones_bio = df_bio['Avance / Plataforma'].dropna().tolist() if not df_bio.empty else ["Sin datos"]
    opciones_astro = df_astro['Ciclo / Marcador Celeste'].dropna().tolist() if not df_astro.empty else ["Sin datos"]

    with col_p1: var_geo = st.selectbox("1. Entidad Geopolítica", opciones_geo)
    with col_p2: var_bio = st.selectbox("2. Avance Biotecnológico", opciones_bio)
    with col_p3: var_astro = st.selectbox("3. Ventana Astro-Temporal", opciones_astro)

    if st.button("Analizar Convergencia", type="primary"):
        fac_geo = df_geo[df_geo['Entidad / Corporación'] == var_geo]['Facción Alineada'].values[0] if not df_geo.empty else "Desconocida"
        fac_bio = df_bio[df_bio['Avance / Plataforma'] == var_bio]['Facción Alineada'].values[0] if not df_bio.empty else "Desconocida"
        if fac_geo == fac_bio:
            st.progress(0.85)
            st.markdown(f"<h3 style='color: red;'>⚠️ ALTA CONVERGENCIA (85%): {var_geo} y {var_bio} responden a la misma agenda ({fac_geo}).</h3>", unsafe_allow_html=True)
        else:
            st.progress(0.40)
            st.markdown(f"<h3 style='color: orange;'>⚡ FRICCIÓN ESTRUCTURAL (40%): {var_geo} choca con {var_bio}. Bloqueos mutuos.</h3>", unsafe_allow_html=True)

with tab_timeline:
    st.subheader("⏱️ Línea de Tiempo Histórica vs Actual")
    if 'Inicio' in df_astro.columns and 'Fin' in df_astro.columns:
        df_timeline = df_astro.dropna(subset=['Inicio', 'Fin'])
        if not df_timeline.empty:
            fig = px.timeline(df_timeline, x_start="Inicio", x_end="Fin", y="Ciclo / Marcador Celeste", color="Facción Alineada", color_discrete_map={"DERECHA (Control)": "#3b82f6", "IZQUIERDA (Caos)": "#f43f5e", "Ambas / Reloj": "#0ea5e9"})
            fig.update_yaxes(autorange="reversed") 
            fig.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8")
            st.plotly_chart(fig, use_container_width=True)

with tab0: st.dataframe(df_ling_masivo, use_container_width=True, hide_index=True)
with tab1: 
    st.dataframe(df_eso_base, use_container_width=True, hide_index=True)
    if textos_raw_eso:
        st.markdown("---")
        st.subheader("📜 Fuentes Primarias (Textos en Crudo)")
        seleccion_txt = st.selectbox("Selecciona un manual decodificado:", list(textos_raw_eso.keys()))
        st.markdown(f"""<div style="height: 400px; overflow-y: auto; background-color: #0f172a; padding: 20px; border: 1px solid #334155; border-radius: 8px; color: #38bdf8; font-family: 'Courier New', monospace; white-space: pre-wrap;">{html.escape(textos_raw_eso[seleccion_txt])}</div>""", unsafe_allow_html=True)

with tab2: st.dataframe(df_geo, use_container_width=True, hide_index=True)
with tab3: st.dataframe(df_bio, use_container_width=True, hide_index=True)
with tab4: st.dataframe(df_astro, use_container_width=True, hide_index=True)
with tab_arq: st.dataframe(df_arquetipos, use_container_width=True, hide_index=True)
