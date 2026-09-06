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
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import tempfile

load_dotenv()

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS ---
st.set_page_config(
    page_title="Matriz Core - Terminal de Inteligencia",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0b0f19; }
    h1, h2, h3 { color: #e2e8f0 !important; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-size: 0.88rem; }
    .stTabs [aria-selected="true"] { color: #38bdf8 !important; border-bottom-color: #38bdf8 !important; }
    
    /* Evitar que los valores métricos se trunquen con puntos suspensivos (...) */
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 1.55rem !important;
        white-space: normal !important;
        word-break: break-word !important;
        overflow: visible !important;
        line-height: 1.2 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        white-space: normal !important;
        font-size: 0.85rem !important;
    }
    .css-1d391kg { background-color: #0f172a; }
    
    @media (max-width: 768px) {
        div[data-testid="stMetricValue"] { font-size: 1.2rem !important; }
        .stTabs [data-baseweb="tab"] { padding: 4px 6px !important; font-size: 0.75rem; }
        .js-plotly-plot .plotly .modebar { orientation: h !important; top: 0 !important; right: 0 !important; }
    }
    </style>
""", unsafe_allow_html=True)

PLOTLY_CONFIG = {
    "responsive": True,
    "displayModeBar": True,
    "displaylogo": False,
    "scrollZoom": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "toggleSpikelines"]
}

# --- 2. RUTAS DINÁMICAS ---
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(DIRECTORIO_ACTUAL, "data")):
    BASE_DIR = DIRECTORIO_ACTUAL
else:
    BASE_DIR = os.path.dirname(DIRECTORIO_ACTUAL)

ruta_procesados     = os.path.join(BASE_DIR, "data", "processed")
ruta_raw_esoterico  = os.path.join(BASE_DIR, "data", "raw", "esoteric")
ruta_base           = os.path.join(ruta_procesados, "Matriz_Core_Sistematizacion_Base.xlsx")
ruta_esoterico      = os.path.join(ruta_procesados, "Vector_1_Esoterico.xlsx")
ruta_geopolitico    = os.path.join(ruta_procesados, "Vector_2_Geopolitico.xlsx")
ruta_biotecnologico = os.path.join(ruta_procesados, "Vector_3_Biotecnologico.xlsx")
ruta_astro          = os.path.join(ruta_procesados, "Vector_4_Astro.xlsx")

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=55)
    st.title("Matriz Core")
    st.caption("Terminal de Inteligencia Ontológica y OSINT")
    
    with st.expander("🧭 Flujo de Correlación y Módulos", expanded=False):
        st.markdown("""
        * **Capa 0 (Fundamento Textual):** Corpus lingüísticos, raíces hebreas/griegas y textos primarios.
        * **Capa 1 (Topología):** Plano Cartesiano de Jonás 4:11, Enjambre y Gobernadores Enoquianos.
        * **Capas 2 y 3 (Anclaje Físico):** Estructuras de control geopolítico y plataformas biológicas.
        * **Capa 4 (Dinámica Temporal):** Reloj astronómico y detección de señales OSINT.
        """)
    
    st.markdown("---")
    st.subheader("⚙️ Parámetros del Sistema")
    input_api_key = st.text_input("NewsAPI Key (Opcional):", value=os.getenv("NEWSAPI_KEY", ""), type="password")
    limite_nodos_texto = st.slider("Límite de versículos en grafo:", 10, 100, 35, help="Controla la densidad y fluidez del grafo de red.")

NEWSAPI_KEY = input_api_key.strip() if input_api_key else os.getenv("NEWSAPI_KEY", "")

# Título conciso
st.title("🔮 MATRIZ CORE // TERMINAL DE INTELIGENCIA")
st.caption("Análisis Ontológico: Jerarquías, Geolocalización, Ratios Demográficos y Radar OSINT")

# --- 4. CARGA DE DATOS ---
@st.cache_data
def cargar_textos_masivos():
    patron = os.path.join(ruta_procesados, "Libro_*_Completo.csv")
    archivos = glob.glob(patron)
    if not archivos: return pd.DataFrame()
    return pd.concat([pd.read_csv(f) for f in archivos], ignore_index=True)

@st.cache_data
def cargar_excel(ruta, hoja, saltar=4):
    if os.path.exists(ruta): 
        try:
            return pd.read_excel(ruta, sheet_name=hoja, skiprows=saltar)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data
def cargar_manuales_raw():
    textos = {}
    if os.path.exists(ruta_raw_esoterico):
        for arch in glob.glob(os.path.join(ruta_raw_esoterico, "*.txt")):
            nombre = os.path.basename(arch).replace(".txt","")
            try:
                with open(arch, 'r', encoding='utf-8') as f: textos[nombre] = f.read()
            except Exception:
                try:
                    with open(arch, 'r', encoding='latin-1') as f: textos[nombre] = f.read()
                except Exception:
                    pass
    return textos

def extraer_cita(texto, palabra_clave, ventana=60):
    idx = texto.upper().find(palabra_clave.upper())
    if idx == -1: return ""
    return f"...{texto[max(0, idx-ventana):min(len(texto), idx+len(palabra_clave)+ventana)].replace(chr(10), ' ').strip()}..."

df_ling_masivo   = cargar_textos_masivos()
df_eso_base      = cargar_excel(ruta_esoterico, "Datos Esotéricos")
df_geo_base      = cargar_excel(ruta_geopolitico, "Estructuras de Control")
df_bio_base      = cargar_excel(ruta_biotecnologico, "Alteraciones Biológicas")
df_astro_base    = cargar_excel(ruta_astro, "Reloj del Sistema")
df_arquetipos    = cargar_excel(ruta_base, "Arquetipos de Facciones")
textos_raw_eso   = cargar_manuales_raw()

# Enriquecimiento de Capa 2 (Infraestructura de Poder Geopolítica)
infraestructura_geopolitica_extra = [
    {"Entidad / Corporación": "BlackRock / Vanguard", "Tipo": "Gestora Financiera Global", "Mecanismo de Control": "Monopolio accionario de infraestructura global y energía", "Facción Alineada": "DERECHA (Control)"},
    {"Entidad / Corporación": "Banco de Pagos Internacionales (BIS)", "Tipo": "Banca Central de Bancos Centrales", "Mecanismo de Control": "Emisión crediticia soberana y protocolos CBDC", "Facción Alineada": "DERECHA (Control)"},
    {"Entidad / Corporación": "DARPA", "Tipo": "Agencia Militar de Proyectos Avanzados", "Mecanismo de Control": "Innovación bélica autónoma e interfaces cognitivas", "Facción Alineada": "DERECHA (Control)"},
    {"Entidad / Corporación": "Palantir Technologies", "Tipo": "Inteligencia Predictiva Militar", "Mecanismo de Control": "Minería masiva de datos y targeting gubernamental", "Facción Alineada": "DERECHA (Control)"},
    {"Entidad / Corporación": "Foro Económico Mundial (WEF)", "Tipo": "Gobernanza Público-Privada", "Mecanismo de Control": "Estandarización de métricas ESG y agenda transhumanista", "Facción Alineada": "DERECHA (Control)"},
    {"Entidad / Corporación": "GCHQ / NSA (Five Eyes)", "Tipo": "Aparato de Señales e Inteligencia", "Mecanismo de Control": "Interceptación de comunicaciones y vigilancia global", "Facción Alineada": "DERECHA (Control)"},
    {"Entidad / Corporación": "OpenAI / Microsoft AI", "Tipo": "Monopolio de Inteligencia Artificial", "Mecanismo de Control": "Moldeo algorítmico cognitivo y automatización sintética", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Entidad / Corporación": "Neuralink", "Tipo": "Interfaz Cerebro-Máquina", "Mecanismo de Control": "Integración bio-digital directa y anulación de privacidad neural", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Entidad / Corporación": "Plataformas ARNm / Pfizer / Moderna", "Tipo": "Biotecnología Génica", "Mecanismo de Control": "Reprogramación celular y respuesta molecular dirigida", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Entidad / Corporación": "TSMC (Semiconductores Taiwán)", "Tipo": "Monopolio de Silicio", "Mecanismo de Control": "Cuello de botella físico para la infraestructura global de cómputo", "Facción Alineada": "DERECHA (Control)"}
]
df_geo = pd.concat([df_geo_base, pd.DataFrame(infraestructura_geopolitica_extra)], ignore_index=True) if not df_geo_base.empty else pd.DataFrame(infraestructura_geopolitica_extra)

# Enriquecimiento de Capa 3 (Biotecnología)
bio_extra = [
    {"Avance / Plataforma": "CRISPR-Cas9 / Edición Genética", "Mecanismo de Operación": "Corte de precisión y recombinación de ADN humano", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Avance / Plataforma": "Quimeras Humano-Animal", "Mecanismo de Operación": "Hibridación interespecie en laboratorio embrionario", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Avance / Plataforma": "Biología Sintética / ARNm", "Mecanismo de Operación": "Instrucción transcriptómica sintética sin vector tradicional", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Avance / Plataforma": "Identificación Biométrica Digital", "Mecanismo de Operación": "Trazabilidad poblacional por iris, rostro y ADN", "Facción Alineada": "DERECHA (Control)"}
]
df_bio = pd.concat([df_bio_base, pd.DataFrame(bio_extra)], ignore_index=True) if not df_bio_base.empty else pd.DataFrame(bio_extra)

# Ventanas Temporales / Astro
nuevos_ciclos_astro = [
    {"Ciclo / Marcador Celeste": "Conjunción Júpiter-Saturno", "Inicio": "2020-12-21", "Fin": "2040-10-31", "Impacto Estructural": "Mutación a Aire. Digitalización del control.", "Facción Alineada": "DERECHA (Control)"},
    {"Ciclo / Marcador Celeste": "Tránsito de Urano en Tauro", "Inicio": "2018-05-15", "Fin": "2026-04-26", "Impacto Estructural": "Disrupción radical de la biología y agricultura.", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Ciclo / Marcador Celeste": "Entrada de Plutón en Acuario", "Inicio": "2023-03-23", "Fin": "2043-03-08", "Impacto Estructural": "Revolución transhumanista, IA general.", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Ciclo / Marcador Celeste": "Conjunción Saturno-Plutón", "Inicio": "2020-01-12", "Fin": "2021-12-31", "Impacto Estructural": "Contracción extrema y fronteras cerradas.", "Facción Alineada": "DERECHA (Control)"},
    {"Ciclo / Marcador Celeste": "Retorno de Plutón (USA)", "Inicio": "2022-02-20", "Fin": "2024-11-19", "Impacto Estructural": "Fractura interna de los imperios occidentales.", "Facción Alineada": "Ambas / Reloj"}
]
df_astro = pd.concat([df_astro_base, pd.DataFrame(nuevos_ciclos_astro)], ignore_index=True) if not df_astro_base.empty else pd.DataFrame(nuevos_ciclos_astro)

# --- 5. MOTOR OSINT CON PASO EXPLÍCITO DE API KEY ---
KEYWORDS_REALES = {
    "Invisibilidad": ["surveillance evasion", "dark money politics"],
    "Terremotos": ["seismic activity tectonic", "earthquake geopolitics"],
    "Secretos": ["classified documents leak", "whistleblower intelligence"],
    "Nigromancia": ["posthumanism digital consciousness", "mind uploading"],
    "Enfermedades": ["pandemic preparedness WHO", "bioweapon research"],
    "Robo": ["intellectual property theft", "corporate espionage"],
    "Ira": ["civil unrest protest crackdown", "political polarization"],
    "Manipulación": ["influence operation social media", "psychological warfare"],
    "Biología": ["synthetic biology DARPA", "gain of function research"],
    "Diplomacia": ["secret diplomacy backchannel", "geopolitical negotiation"],
    "Guerra": ["proxy war escalation", "military buildup conflict"],
    "Milicia": ["private military contractor PMC", "mercenary operation"],
    "Materialismo": ["central bank digital currency", "asset seizure"],
    "Espionaje": ["intelligence agency espionage", "cyber surveillance state"],
    "Rebelión e Hibridación Genética": ["human animal hybrid research", "chimera embryo lab"],
    "Banca central y monopolio de la emisión": ["central bank monopoly", "currency issuance control"],
    "default": ["geopolitics power elite", "world order control"]
}

@st.cache_data(ttl=3600)
def buscar_noticias_entidad(funcion: str, nombre: str, api_key_usuario: str) -> list:
    keywords = KEYWORDS_REALES.get(funcion, KEYWORDS_REALES["default"])
    query = " OR ".join(f'"{k}"' for k in keywords[:2])
    
    if api_key_usuario:
        try:
            resp = requests.get("https://newsapi.org/v2/everything", params={
                "q": query, "language": "en", "sortBy": "publishedAt", "pageSize": 5,
                "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"), "apiKey": api_key_usuario
            }, timeout=6)
            data = resp.json()
            if data.get("status") == "ok" and data.get("articles"):
                return [{
                    "titulo": a.get("title", ""),
                    "descripcion": a.get("description", ""),
                    "url": a.get("url", "#"),
                    "fuente": a.get("source", {}).get("name", "NewsAPI"),
                    "fecha": a.get("publishedAt", "")[:10]
                } for a in data["articles"][:5]]
        except Exception:
            pass
            
    # Fallback por RSS
    try:
        kw = keywords[0] if keywords else "geopolitics"
        rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(kw)}&hl=en&gl=US&ceid=US:en"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        req = urllib.request.Request(rss_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            xml_data = r.read()
        root = ET.fromstring(xml_data)
        return [{
            "titulo": i.find("title").text if i.find("title") is not None else "",
            "descripcion": i.find("description").text if i.find("description") is not None else "",
            "url": i.find("link").text if i.find("link") is not None else "#",
            "fuente": "Google News RSS",
            "fecha": i.find("pubDate").text[:16] if i.find("pubDate") is not None else ""
        } for i in root.findall(".//item")[:5]]
    except Exception:
        return []

# --- 6. TOPOLOGÍA SEMÁNTICA Y ENTIDADES COMPLETAS ---
CUADRANTES_PLANO = {
    "Q1": {"nombre": "Control con Límites", "eje_x": 1, "eje_y": 1, "raices": ["YAMIN_DEXIOS", "BEYN_KRIMA"], "descripcion": "Autoridad ejercida mediante delimitación y separación precisa. Ley, ritual, jerarquía.", "faccion": "DERECHA (Control)", "color": "#1d4ed8"},
    "Q2": {"nombre": "Autoridad por Discernimiento", "eje_x": 1, "eje_y": -1, "raices": ["YAMIN_DEXIOS", "YADA_GINOSKO"], "descripcion": "Poder que emana del conocimiento encarnado y sabiduría operativa directa.", "faccion": "DERECHA (Control)", "color": "#2563eb"},
    "Q3": {"nombre": "Caos Contenido", "eje_x": -1, "eje_y": 1, "raices": ["SMOL_ARISTEROS", "BEYN_KRIMA"], "descripcion": "Frontera violada pero reconocida. Transgresión consciente del límite.", "faccion": "IZQUIERDA (Caos)", "color": "#be123c"},
    "Q4": {"nombre": "Indistinción Total", "eje_x": -1, "eje_y": -1, "raices": ["SMOL_ARISTEROS", "YADA_GINOSKO"], "descripcion": "Colapso de la función discriminatoria. Hibridación pura (Jonás 4:11).", "faccion": "IZQUIERDA (Caos)", "color": "#e11d48"},
    "UMBRAL": {"nombre": "Zona de Frontera", "eje_x": 0, "eje_y": 0, "raices": ["BEYN_KRIMA"], "descripcion": "Espacio intermedio neutro entre jurisdicciones.", "faccion": "Ambas / Umbral", "color": "#0ea5e9"}
}

# 91 GOBERNADORES ENOQUIANOS COMPLETOS (John Dee, 1584)
GOBERNADORES_91 = [
    {"nombre":"Occodon","aethyr":"TEX","num":1,"jurisdiccion":"Bretaña / Islas del Norte","funcion":"Custodia del primer umbral, registro de entrada","cuadrante":"Q1","lat":51.5,"lon":-0.1,"legiones":30},
    {"nombre":"Pascomb","aethyr":"TEX","num":2,"jurisdiccion":"Germania Occidental","funcion":"Registro perpetuo de acciones y consecuencias","cuadrante":"Q1","lat":50.9,"lon":6.9,"legiones":30},
    {"nombre":"Valgars","aethyr":"TEX","num":3,"jurisdiccion":"Galia / Francia","funcion":"Aplicación de consecuencias jurisdiccionales","cuadrante":"Q1","lat":48.8,"lon":2.3,"legiones":30},
    {"nombre":"Doagnis","aethyr":"RII","num":4,"jurisdiccion":"Egipto / Valle del Nilo","funcion":"Administración de flujos de poder entre facciones","cuadrante":"Q1","lat":30.0,"lon":31.2,"legiones":30},
    {"nombre":"Pacasna","aethyr":"RII","num":5,"jurisdiccion":"Mesopotamia / Tigris-Éufrates","funcion":"Separación y delimitación de jurisdicciones","cuadrante":"Q1","lat":33.3,"lon":44.4,"legiones":30},
    {"nombre":"Dialoia","aethyr":"RII","num":6,"jurisdiccion":"Persia / Irán","funcion":"Diálogo entre órdenes jerárquicos distintos","cuadrante":"Q2","lat":35.6,"lon":51.3,"legiones":30},
    {"nombre":"Samapha","aethyr":"BAG","num":7,"jurisdiccion":"Arabia / Península Arábiga","funcion":"Consolidación de estructuras de autoridad","cuadrante":"Q1","lat":24.7,"lon":46.7,"legiones":30},
    {"nombre":"Virooli","aethyr":"BAG","num":8,"jurisdiccion":"India / Subcontinente","funcion":"Mantenimiento de orden en territorios extensos","cuadrante":"Q1","lat":28.6,"lon":77.2,"legiones":30},
    {"nombre":"Andispi","aethyr":"BAG","num":9,"jurisdiccion":"Escitia / Asia Central","funcion":"Control de fronteras nómadas e inestables","cuadrante":"Q2","lat":43.0,"lon":68.0,"legiones":30},
    {"nombre":"Thotanp","aethyr":"ZAA","num":10,"jurisdiccion":"Etiopía / Cuerno de África","funcion":"Visión de largo plazo, planificación de ciclos","cuadrante":"Q2","lat":9.0,"lon":38.7,"legiones":30},
    {"nombre":"Axziarg","aethyr":"ZAA","num":11,"jurisdiccion":"Anatolia / Asia Menor","funcion":"Análisis estratégico de estructuras en conflicto","cuadrante":"Q2","lat":39.9,"lon":32.8,"legiones":30},
    {"nombre":"Pothnir","aethyr":"ZAA","num":12,"jurisdiccion":"Grecia / Mar Egeo","funcion":"Discernimiento filosófico aplicado al gobierno","cuadrante":"Q2","lat":37.9,"lon":23.7,"legiones":30},
    {"nombre":"Lazdixi","aethyr":"DES","num":13,"jurisdiccion":"Fenicia / Levante costero","funcion":"Memoria institucional, archivo de pactos y tratados","cuadrante":"Q1","lat":33.5,"lon":35.3,"legiones":30},
    {"nombre":"Nocamal","aethyr":"DES","num":14,"jurisdiccion":"Cartago / Norte de África","funcion":"Transmisión de conocimiento entre generaciones de poder","cuadrante":"Q2","lat":36.8,"lon":10.1,"legiones":30},
    {"nombre":"Tiarpax","aethyr":"DES","num":15,"jurisdiccion":"Hispania / Iberia","funcion":"Expansión ordenada de jurisdicción territorial","cuadrante":"Q1","lat":40.4,"lon":-3.7,"legiones":30},
    {"nombre":"Saxtomp","aethyr":"VTI","num":16,"jurisdiccion":"Britania / Stonehenge","funcion":"Calibración de ciclos temporales y astronómicos","cuadrante":"Q2","lat":51.1,"lon":-1.8,"legiones":30},
    {"nombre":"Vavaamp","aethyr":"VTI","num":17,"jurisdiccion":"Escandinavia / Norte","funcion":"Medición de fuerzas entre órdenes en tensión","cuadrante":"Q1","lat":59.9,"lon":10.7,"legiones":30},
    {"nombre":"Zirzird","aethyr":"VTI","num":18,"jurisdiccion":"Rusia / Estepa póntica","funcion":"Instrumentos de vigilancia y detección temprana","cuadrante":"Q1","lat":55.7,"lon":37.6,"legiones":30},
    {"nombre":"Omagrap","aethyr":"NIA","num":19,"jurisdiccion":"Polonia / Europa del Este","funcion":"Comunicación vertical entre capas del sistema","cuadrante":"Q2","lat":52.2,"lon":21.0,"legiones":30},
    {"nombre":"Zildron","aethyr":"NIA","num":20,"jurisdiccion":"Bohemia / Europa Central","funcion":"Codificación de mensajes entre rangos","cuadrante":"Q1","lat":50.0,"lon":14.4,"legiones":30},
    {"nombre":"Parziba","aethyr":"NIA","num":21,"jurisdiccion":"Hungría / Cuenca del Danubio","funcion":"Transmisión de instrucciones sin pérdida semántica","cuadrante":"Q2","lat":47.4,"lon":19.0,"legiones":30},
    {"nombre":"Ronoamb","aethyr":"TOR","num":22,"jurisdiccion":"Anatolia / Frigia","funcion":"Custodia de recursos estratégicos y minerales","cuadrante":"Q1","lat":39.0,"lon":30.5,"legiones":30},
    {"nombre":"Onizimp","aethyr":"TOR","num":23,"jurisdiccion":"Siria / Mesopotamia Alta","funcion":"Acumulación y redistribución controlada de capital","cuadrante":"Q1","lat":36.2,"lon":37.1,"legiones":30},
    {"nombre":"Zaxanin","aethyr":"TOR","num":24,"jurisdiccion":"Chipre / Mediterráneo Oriental","funcion":"Gestión de rutas comerciales y flujos de valor","cuadrante":"Q2","lat":35.1,"lon":33.3,"legiones":30},
    {"nombre":"Odraxti","aethyr":"LIN","num":25,"jurisdiccion":"Babilonia / Código de Hammurabi","funcion":"Codificación y aplicación de sistemas legales","cuadrante":"Q1","lat":32.5,"lon":44.4,"legiones":30},
    {"nombre":"Genadol","aethyr":"LIN","num":26,"jurisdiccion":"Roma / Italia","funcion":"Derecho institucional, jurisprudencia y precedente","cuadrante":"Q1","lat":41.9,"lon":12.4,"legiones":30},
    {"nombre":"Aspiaon","aethyr":"LIN","num":27,"jurisdiccion":"Judea / Jerusalén","funcion":"Ley sagrada, regulación de lo puro e impuro","cuadrante":"Q1","lat":31.7,"lon":35.2,"legiones":30},
    {"nombre":"Toantom","aethyr":"ASP","num":28,"jurisdiccion":"Egipto / Alejandría","funcion":"Sistemas de vigilancia e inteligencia centralizada","cuadrante":"Q1","lat":31.2,"lon":29.9,"legiones":30},
    {"nombre":"Vixpalg","aethyr":"ASP","num":29,"jurisdiccion":"Partia / Irán Oriental","funcion":"Red de informantes y agentes encubiertos","cuadrante":"Q2","lat":33.5,"lon":60.0,"legiones":30},
    {"nombre":"Oxlopar","aethyr":"ASP","num":30,"jurisdiccion":"Macedonia / Grecia del Norte","funcion":"Contraespionaje y purga de infiltraciones","cuadrante":"Q1","lat":40.6,"lon":22.9,"legiones":30},
    {"nombre":"Zarzilg","aethyr":"CHR","num":31,"jurisdiccion":"Caldea / Astronomía babilónica","funcion":"Administración de ciclos temporales y calendarios","cuadrante":"Q2","lat":30.0,"lon":46.0,"legiones":30},
    {"nombre":"Ioaltap","aethyr":"CHR","num":32,"jurisdiccion":"Egipto / Karnak","funcion":"Sincronización de rituales con ciclos astronómicos","cuadrante":"Q1","lat":25.7,"lon":32.6,"legiones":30},
    {"nombre":"Ivonph","aethyr":"CHR","num":33,"jurisdiccion":"Stonehenge / Bretaña","funcion":"Marcadores de equinoccios y solsticios como umbrales","cuadrante":"UMBRAL","lat":51.1,"lon":-1.8,"legiones":30},
    {"nombre":"Tedoand","aethyr":"POP","num":34,"jurisdiccion":"India / Punjab","funcion":"Control demográfico y administración de poblaciones","cuadrante":"Q1","lat":31.5,"lon":74.3,"legiones":30},
    {"nombre":"Vivipos","aethyr":"POP","num":35,"jurisdiccion":"China / Valle del Amarillo","funcion":"Censos, clasificación y registro de poblaciones","cuadrante":"Q1","lat":34.7,"lon":113.6,"legiones":30},
    {"nombre":"Uvivon","aethyr":"POP","num":36,"jurisdiccion":"Mesoamérica / Yucatán","funcion":"Regulación de roles sociales y estratificación","cuadrante":"Q1","lat":20.9,"lon":-89.6,"legiones":30},
    {"nombre":"Zinggen","aethyr":"ZEN","num":37,"jurisdiccion":"Alejandría / Biblioteca","funcion":"Administración del conocimiento técnico y científico","cuadrante":"Q2","lat":31.2,"lon":29.9,"legiones":30},
    {"nombre":"Alpudus","aethyr":"ZEN","num":38,"jurisdiccion":"Bagdad / Casa de la Sabiduría","funcion":"Traducción y preservación de corpus filosóficos","cuadrante":"Q2","lat":33.3,"lon":44.4,"legiones":30},
    {"nombre":"Taoagla","aethyr":"ZEN","num":39,"jurisdiccion":"Toledo / España Medieval","funcion":"Síntesis de tradiciones del conocimiento en poder","cuadrante":"Q2","lat":39.8,"lon":-4.0,"legiones":30},
    {"nombre":"Sigmorf","aethyr":"TAN","num":40,"jurisdiccion":"Westfalia / Europa","funcion":"Formación y mantenimiento de tratados entre potencias","cuadrante":"Q1","lat":51.9,"lon":7.6,"legiones":30},
    {"nombre":"Aydropt","aethyr":"TAN","num":41,"jurisdiccion":"Viena / Imperio Austro-Húngaro","funcion":"Diplomacia de alto nivel y protocolo de alianzas","cuadrante":"Q1","lat":48.2,"lon":16.3,"legiones":30},
    {"nombre":"Toantomv","aethyr":"TAN","num":42,"jurisdiccion":"Versalles / Francia","funcion":"Etiqueta del poder, formalización de jerarquías","cuadrante":"Q1","lat":48.8,"lon":2.1,"legiones":30},
    {"nombre":"Lazdixr","aethyr":"LEA","num":43,"jurisdiccion":"Atenas / Agora","funcion":"Legitimación del liderazgo ante poblaciones","cuadrante":"Q2","lat":37.9,"lon":23.7,"legiones":30},
    {"nombre":"Notahon","aethyr":"LEA","num":44,"jurisdiccion":"Roma / Foro Romano","funcion":"Oratoria y persuasión al servicio del orden","cuadrante":"Q2","lat":41.8,"lon":12.4,"legiones":30},
    {"nombre":"Vastrim","aethyr":"LEA","num":45,"jurisdiccion":"Constantinopla / Bizancio","funcion":"Unificación de autoridad espiritual y temporal","cuadrante":"Q1","lat":41.0,"lon":28.9,"legiones":30},
    {"nombre":"Tahamdo","aethyr":"OXO","num":46,"jurisdiccion":"Esparta / Grecia","funcion":"Estructuras de obediencia absoluta y disciplina","cuadrante":"Q1","lat":37.0,"lon":22.4,"legiones":30},
    {"nombre":"Nociabi","aethyr":"OXO","num":47,"jurisdiccion":"Prusia / Germania","funcion":"Jerarquía militar y cadena de mando","cuadrante":"Q1","lat":52.5,"lon":13.4,"legiones":30},
    {"nombre":"Tastoxo","aethyr":"OXO","num":48,"jurisdiccion":"Japón / Shogunato","funcion":"Honor y lealtad como mecanismos de control","cuadrante":"Q2","lat":35.6,"lon":139.6,"legiones":30},
    {"nombre":"Cucarpt","aethyr":"UTA","num":49,"jurisdiccion":"Rubicón / Italia Norte","funcion":"Gestión de puntos de no retorno y umbrales críticos","cuadrante":"UMBRAL","lat":44.1,"lon":12.2,"legiones":30},
    {"nombre":"Lazindor","aethyr":"UTA","num":50,"jurisdiccion":"Termópilas / Grecia","funcion":"Defensa de pasos estratégicos y cuellos de botella","cuadrante":"Q1","lat":38.8,"lon":22.5,"legiones":30},
    {"nombre":"Sigmorfv","aethyr":"UTA","num":51,"jurisdiccion":"Paso de Bering / Norte","funcion":"Control de migraciones y desplazamientos poblacionales","cuadrante":"Q1","lat":65.5,"lon":-168.0,"legiones":30},
    {"nombre":"Gebabal","aethyr":"ZIM","num":52,"jurisdiccion":"Venecia / Banca Medieval","funcion":"Creación y regulación de sistemas de valor","cuadrante":"Q1","lat":45.4,"lon":12.3,"legiones":30},
    {"nombre":"Agirath","aethyr":"ZIM","num":53,"jurisdiccion":"Ámsterdam / VOC","funcion":"Instrumentos financieros y deuda como control","cuadrante":"Q2","lat":52.3,"lon":4.9,"legiones":30},
    {"nombre":"Zinggenv","aethyr":"ZIM","num":54,"jurisdiccion":"Londres / City","funcion":"Banca central y monopolio de la emisión","cuadrante":"Q1","lat":51.5,"lon":-0.08,"legiones":30},
    {"nombre":"Tafitoal","aethyr":"LOE","num":55,"jurisdiccion":"Sumer / Escritura cuneiforme","funcion":"Creación de sistemas de escritura como tecnología de poder","cuadrante":"Q2","lat":31.9,"lon":45.8,"legiones":30},
    {"nombre":"Iolana","aethyr":"LOE","num":56,"jurisdiccion":"Egipto / Escritura jeroglífica","funcion":"Codificación del poder en sistemas simbólicos","cuadrante":"Q2","lat":25.6,"lon":32.5,"legiones":30},
    {"nombre":"Palam","aethyr":"LOE","num":57,"jurisdiccion":"Fenicia / Alfabeto","funcion":"Democratización controlada del lenguaje escrito","cuadrante":"UMBRAL","lat":34.0,"lon":35.6,"legiones":30},
    {"nombre":"Molpand","aethyr":"IKH","num":58,"jurisdiccion":"Roma / Vías Romanas","funcion":"Infraestructura de movilidad y control territorial","cuadrante":"Q1","lat":41.9,"lon":12.4,"legiones":30},
    {"nombre":"Vsnarda","aethyr":"IKH","num":59,"jurisdiccion":"China / Gran Muralla","funcion":"Arquitectura defensiva y demarcación de fronteras","cuadrante":"Q1","lat":40.4,"lon":116.5,"legiones":30},
    {"nombre":"Ponodol","aethyr":"IKH","num":60,"jurisdiccion":"Egipto / Pirámides","funcion":"Monumentalización del poder como señal de permanencia","cuadrante":"Q1","lat":29.9,"lon":31.1,"legiones":30},
    {"nombre":"Lexarph","aethyr":"ZAX","num":61,"jurisdiccion":"El Abismo","funcion":"Guardián del umbral entre el ser y el no-ser","cuadrante":"UMBRAL","lat":0.0,"lon":0.0,"legiones":30},
    {"nombre":"Comanan","aethyr":"ZAX","num":62,"jurisdiccion":"El Abismo","funcion":"Disolución de estructuras que cruzaron el umbral","cuadrante":"UMBRAL","lat":0.0,"lon":0.5,"legiones":30},
    {"nombre":"Tabitom","aethyr":"ZAX","num":63,"jurisdiccion":"El Abismo","funcion":"Reintegración post-disolución en nueva forma","cuadrante":"UMBRAL","lat":0.0,"lon":-0.5,"legiones":30},
    {"nombre":"Orcanir","aethyr":"ZIP","num":64,"jurisdiccion":"Asiria / Nínive","funcion":"Tecnología bélica y proyección de fuerza ordenada","cuadrante":"Q1","lat":36.3,"lon":43.1,"legiones":30},
    {"nombre":"Chialps","aethyr":"ZIP","num":65,"jurisdiccion":"Mongolia / Imperio Mongol","funcion":"Estrategia de expansión y consolidación territorial","cuadrante":"Q2","lat":47.9,"lon":106.9,"legiones":30},
    {"nombre":"Toantomz","aethyr":"ZIP","num":66,"jurisdiccion":"Prusia / Estado Mayor","funcion":"Doctrina militar y aplicación sistemática de la fuerza","cuadrante":"Q1","lat":52.5,"lon":13.4,"legiones":30},
    {"nombre":"Zamfres","aethyr":"ZID","num":67,"jurisdiccion":"Israel / Tribus","funcion":"Custodia de linajes y pureza genealógica","cuadrante":"Q1","lat":31.7,"lon":35.2,"legiones":30},
    {"nombre":"Todnaon","aethyr":"ZID","num":68,"jurisdiccion":"Esparta / Eugenesia","funcion":"Selección y preservación de rasgos en poblaciones","cuadrante":"Q2","lat":37.0,"lon":22.4,"legiones":30},
    {"nombre":"Pristac","aethyr":"ZID","num":69,"jurisdiccion":"Roma / Gens Patriciae","funcion":"Aristocracia hereditaria como mecanismo de continuidad","cuadrante":"Q1","lat":41.9,"lon":12.5,"legiones":30},
    {"nombre":"Obmacas","aethyr":"DEO","num":70,"jurisdiccion":"Vaticano / Roma","funcion":"Unificación de autoridad espiritual como poder político","cuadrante":"Q1","lat":41.9,"lon":12.4,"legiones":30},
    {"nombre":"Genadolv","aethyr":"DEO","num":71,"jurisdiccion":"Constantinopla / Patriarcado","funcion":"Canon, ortodoxia y expulsión de lo heterodoxo","cuadrante":"Q1","lat":41.0,"lon":28.9,"legiones":30},
    {"nombre":"Asmorno","aethyr":"DEO","num":72,"jurisdiccion":"La Meca / Islam","funcion":"Ley sagrada como código total de organización social","cuadrante":"Q1","lat":21.3,"lon":39.8,"legiones":30},
    {"nombre":"Saziami","aethyr":"MAZ","num":73,"jurisdiccion":"Manchester / Revolución Industrial","funcion":"Control de medios de producción y cadenas de valor","cuadrante":"Q1","lat":53.4,"lon":-2.2,"legiones":30},
    {"nombre":"Mathvla","aethyr":"MAZ","num":74,"jurisdiccion":"Pittsburgh / Acero","funcion":"Monopolio de recursos estratégicos industriales","cuadrante":"Q1","lat":40.4,"lon":-79.9,"legiones":30},
    {"nombre":"Orpamb","aethyr":"MAZ","num":75,"jurisdiccion":"Bakú / Petróleo","funcion":"Control de fuentes energéticas como palanca geopolítica","cuadrante":"Q2","lat":40.4,"lon":49.8,"legiones":30},
    {"nombre":"Caosgi","aethyr":"LIT","num":76,"jurisdiccion":"Gutenberg / Maguncia","funcion":"Control de medios de reproducción y difusión","cuadrante":"Q1","lat":49.9,"lon":8.2,"legiones":30},
    {"nombre":"Lusanahe","aethyr":"LIT","num":77,"jurisdiccion":"Fleet Street / Londres","funcion":"Narrativa hegemónica y agenda setting","cuadrante":"Q2","lat":51.5,"lon":-0.1,"legiones":30},
    {"nombre":"Sodalzt","aethyr":"LIT","num":78,"jurisdiccion":"Silicon Valley / Digital","funcion":"Algoritmos de filtrado y curación de realidad","cuadrante":"Q2","lat":37.3,"lon":-122.0,"legiones":30},
    {"nombre":"Thotanpv","aethyr":"PAZ","num":79,"jurisdiccion":"Pax Romana / Imperio","funcion":"Mantenimiento del statu quo como tecnología de poder","cuadrante":"Q1","lat":41.9,"lon":12.4,"legiones":30},
    {"nombre":"Axziargv","aethyr":"PAZ","num":80,"jurisdiccion":"Bretton Woods / Post-WWII","funcion":"Institucionalización del orden internacional","cuadrante":"Q1","lat":44.3,"lon":-71.4,"legiones":30},
    {"nombre":"Pothnirv","aethyr":"PAZ","num":81,"jurisdiccion":"Naciones Unidas / NY","funcion":"Multilateralismo como mecanismo de contención","cuadrante":"Q1","lat":40.7,"lon":-74.0,"legiones":30},
    {"nombre":"Samaphav","aethyr":"ZOM","num":82,"jurisdiccion":"Amazonas / Biodiversidad","funcion":"Custodia del orden biológico y las taxonomías naturales","cuadrante":"Q1","lat":-3.4,"lon":-65.0,"legiones":30},
    {"nombre":"Virooliv","aethyr":"ZOM","num":83,"jurisdiccion":"Galápagos / Darwin","funcion":"Regulación de la selección y adaptación controlada","cuadrante":"Q2","lat":-0.9,"lon":-89.6,"legiones":30},
    {"nombre":"Andispiv","aethyr":"ZOM","num":84,"jurisdiccion":"Mendel / Genética (Brno)","funcion":"Herencia como código de transmisión de orden","cuadrante":"Q2","lat":49.1,"lon":16.6,"legiones":30},
    {"nombre":"Doagnisv","aethyr":"ARN","num":85,"jurisdiccion":"Platón / Atenas","funcion":"Geometría como fundamento del orden cósmico","cuadrante":"Q1","lat":37.9,"lon":23.7,"legiones":30},
    {"nombre":"Pacasnav","aethyr":"ARN","num":86,"jurisdiccion":"Pitágoras / Crotona","funcion":"Número y proporción como lenguaje del control","cuadrante":"Q2","lat":39.0,"lon":17.1,"legiones":30},
    {"nombre":"Dialoiav","aethyr":"ARN","num":87,"jurisdiccion":"Kepler / Praga","funcion":"Armonía de esferas como modelo de jerarquía perfecta","cuadrante":"Q2","lat":50.0,"lon":14.4,"legiones":30},
    {"nombre":"Occodonl","aethyr":"LIL","num":88,"jurisdiccion":"LIL / Sin geografía terrestre","funcion":"Fuente primordial de toda autoridad en el sistema","cuadrante":"Q1","lat":55.0,"lon":25.0,"legiones":30},
    {"nombre":"Pascombl","aethyr":"LIL","num":89,"jurisdiccion":"LIL / Sin geografía terrestre","funcion":"Registro eterno, el libro que no se borra","cuadrante":"Q1","lat":56.0,"lon":30.0,"legiones":30},
    {"nombre":"Valgarsl","aethyr":"LIL","num":90,"jurisdiccion":"LIL / Sin geografía terrestre","funcion":"Ejecución final de la voluntad del sistema completo","cuadrante":"Q1","lat":54.0,"lon":20.0,"legiones":30},
    {"nombre":"Lrasd","aethyr":"LIL","num":91,"jurisdiccion":"LIL / Sin geografía terrestre","funcion":"El sellado — cierre del ciclo completo del sistema","cuadrante":"Q1","lat":57.0,"lon":35.0,"legiones":30},
]

# 72 DEMONIOS DE LA GOETIA COMPLETOS
goetia_72 = [
    ("Bael","Rey",66,"Invisibilidad"),("Agares","Duque",31,"Terremotos"),("Vassago","Príncipe",26,"Secretos"),("Samigina","Marqués",30,"Nigromancia"),("Marbas","Presidente",36,"Enfermedades"),("Valefor","Duque",10,"Robo"),("Amon","Marqués",40,"Ira"),("Barbatos","Duque",30,"Tesoros"),("Paimon","Rey",200,"Manipulación"),("Buer","Presidente",50,"Biología"),
    ("Gusion","Duque",40,"Diplomacia"),("Sitri","Príncipe",60,"Lujuria"),("Beleth","Rey",85,"Pasiones"),("Leraje","Marqués",30,"Guerra"),("Eligos","Duque",60,"Milicia"),("Zepar","Duque",26,"Mutación"),("Botis","Presidente",60,"Facciones"),("Bathin","Duque",30,"Proyección"),("Sallos","Duque",30,"Alteración sentimental"),("Purson","Rey",22,"Materialismo"),
    ("Marax","Conde",30,"Astronomía"),("Ipos","Príncipe",36,"Elocuencia"),("Aim","Duque",26,"Caos Urbano"),("Naberius","Marqués",19,"Astucia"),("Glasya-Labolas","Presidente",36,"Asesinatos"),("Bune","Duque",30,"Fraude"),("Ronove","Marqués",19,"Humillación"),("Berith","Duque",26,"Transmutación"),("Astaroth","Duque",40,"Filosofía"),("Forneus","Marqués",29,"Idiomas"),
    ("Foras","Presidente",29,"Tesoros"),("Asmoday","Rey",72,"Destrucción Genética"),("Gaap","Príncipe",66,"Robo intelectual"),("Furfur","Conde",26,"Tormentas"),("Marchosias","Marqués",30,"Revoluciones"),("Stolas","Príncipe",26,"Venenos"),("Phenex","Marqués",20,"Obediencia"),("Halphas","Conde",26,"Armamento"),("Malphas","Presidente",40,"Espionaje"),("Raum","Conde",30,"Robo de dignidades"),
    ("Focalor","Duque",30,"Asesinatos navales"),("Vepar","Duque",29,"Plagas"),("Sabnock","Marqués",50,"Gangrena"),("Shax","Marqués",30,"Anulación de sentidos"),("Vine","Rey",36,"Destrucción de muros"),("Bifrons","Conde",6,"Necromancia"),("Uvall","Duque",37,"Futuro"),("Haagenti","Presidente",33,"Biología Sintética"),("Crocell","Duque",48,"Aguas termales"),("Furcas","Caballero",20,"Lógica"),
    ("Balam","Rey",40,"Engaño Masivo"),("Alloces","Duque",36,"Arquitectura bélica"),("Camio","Presidente",30,"Lenguaje animal"),("Murmur","Duque",30,"Filosofía restrictiva"),("Orobas","Príncipe",20,"Verdad inalterable"),("Gremory","Duque",26,"Ilícitos"),("Ose","Presidente",30,"Transformación"),("Amy","Presidente",36,"Manipulación de voluntad"),("Oriax","Marqués",30,"Títulos"),("Vapula","Duque",36,"Ciencias oscuras"),
    ("Zagan","Rey",33,"Alquimia"),("Volac","Presidente",38,"Descubrimientos"),("Andras","Marqués",30,"Polarización y Discordia"),("Haures","Duque",36,"Venganza"),("Andrealphus","Marqués",30,"Mutación animal"),("Cimejes","Marqués",20,"Gramática"),("Amdusias","Duque",29,"Control natural"),("Belial","Rey",80,"Favores políticos"),("Decarabia","Marqués",30,"Ilusiones"),("Seere","Príncipe",26,"Teletransportación"),("Dantalion","Duque",36,"Control de pensamientos"),("Andromalius","Conde",36,"Castigo a conspiradores")
]

ENTIDADES_POR_LEGION = 6666
comandantes = []
nodos_por_clase = {}
geo_map_data = []

random.seed(42)

nodos_goetia = [("Babilonia (Hillah, Irak)",32.5363,44.4208),("Persia (Teherán, Irán)",35.6892,51.3890),("Egipto (El Cairo)",30.0444,31.2357),("Fenicia / Sidón (Líbano)",33.5571,35.3730),("Desierto de Arabia (Riad, AS)",24.7136,46.6753),("Sodoma (Mar Muerto, Jordania)",31.3333,35.5000)]
nodos_enoc   = [("Britannia (Londres, UK)",51.5074,-0.1278),("Sarmatia (Moscú, Rusia)",55.7558,37.6173),("Italia (Roma)",41.9028,12.4964),("Gallia (París, Francia)",48.8566,2.3522),("Mesopotamia (Damasco, Siria)",33.5138,36.2765),("Bactriana (Nueva Delhi, India)",28.6139,77.2090)]

# Ingesta Goetia
for nombre, rango, legiones, funcion in goetia_72:
    raiz = "SMOL_ARISTEROS" if rango in ["Rey","Marqués","Conde"] else "YADA_GINOSKO"
    id_nodo = f"{rango} {nombre}"
    lugar = random.choice(nodos_goetia)
    cuad = "Q4" if rango in ["Rey","Marqués"] else "Q3"
    entidades = legiones * ENTIDADES_POR_LEGION
    comandantes.append({"IdNodo":id_nodo,"Comandante":nombre,"Faccion":"IZQUIERDA (Caos)","Raiz":raiz,"Rango":rango,"Legiones":legiones,"Entidades":entidades,"Legiones_Str":f"{legiones} Legiones / {entidades:,} ent.","Funcion":funcion,"OSINT":funcion,"Ubicacion":lugar[0],"Lat":lugar[1],"Lon":lugar[2],"Cuadrante":cuad,"Aethyr":"Ars Goetia"})
    if rango not in nodos_por_clase: nodos_por_clase[rango]=[]
    nodos_por_clase[rango].append(id_nodo)
    geo_map_data.append({"Comandante":id_nodo,"Nombre":nombre,"Faccion":"IZQUIERDA (Caos)","Rango":rango,"Lat":lugar[1],"Lon":lugar[2],"Ubicacion":lugar[0],"Legiones":legiones,"Entidades":entidades,"Cuadrante":cuad,"Fuente":"Ars Goetia"})

# Reyes Elementales
reyes_enoc = [("Bataivah","Rey Elemental","Aire",100),("Raagiosl","Rey Elemental","Agua",100),("Iczhihal","Rey Elemental","Tierra",100),("Edaiel","Rey Elemental","Fuego",100)]
for nombre, rango, dominio, legiones in reyes_enoc:
    id_nodo = f"{rango} {nombre}"
    lugar = random.choice(nodos_enoc)
    entidades = legiones * ENTIDADES_POR_LEGION
    funcion_rey = f"Gobierno del {dominio} — administración elemental total"
    comandantes.append({"IdNodo":id_nodo,"Comandante":nombre,"Faccion":"DERECHA (Control)","Raiz":"YAMIN_DEXIOS","Rango":rango,"Legiones":legiones,"Entidades":entidades,"Legiones_Str":f"{legiones} Legiones / {entidades:,} ent.","Funcion":funcion_rey,"OSINT":funcion_rey,"Ubicacion":lugar[0],"Lat":lugar[1],"Lon":lugar[2],"Cuadrante":"Q1","Aethyr":"LIL"})
    if rango not in nodos_por_clase: nodos_por_clase[rango]=[]
    nodos_por_clase[rango].append(id_nodo)
    geo_map_data.append({"Comandante":id_nodo,"Nombre":nombre,"Faccion":"DERECHA (Control)","Rango":rango,"Lat":lugar[1],"Lon":lugar[2],"Ubicacion":lugar[0],"Legiones":legiones,"Entidades":entidades,"Cuadrante":"Q1","Fuente":"Liber Scientiae"})

# 24 Ancianos
for i in range(24):
    nombre = f"Anciano {i+1}"
    id_nodo = f"Anciano {nombre}"
    lugar = random.choice(nodos_enoc)
    legiones, entidades = 30, 30 * ENTIDADES_POR_LEGION
    funcion_anc = "Vigilancia sin intervención — registro eterno del sistema"
    comandantes.append({"IdNodo":id_nodo,"Comandante":nombre,"Faccion":"DERECHA (Control)","Raiz":"BEYN_KRIMA","Rango":"Anciano","Legiones":legiones,"Entidades":entidades,"Legiones_Str":f"{legiones} Legiones / {entidades:,} ent.","Funcion":funcion_anc,"OSINT":funcion_anc,"Ubicacion":lugar[0],"Lat":lugar[1],"Lon":lugar[2],"Cuadrante":"Q1","Aethyr":"LIL-ARN"})
    if "Anciano" not in nodos_por_clase: nodos_por_clase["Anciano"]=[]
    nodos_por_clase["Anciano"].append(id_nodo)
    geo_map_data.append({"Comandante":id_nodo,"Nombre":nombre,"Faccion":"DERECHA (Control)","Rango":"Anciano","Lat":lugar[1],"Lon":lugar[2],"Ubicacion":lugar[0],"Legiones":legiones,"Entidades":entidades,"Cuadrante":"Q1","Fuente":"Apocalipsis 4"})

# 91 Gobernadores Enoquianos
for g in GOBERNADORES_91:
    id_nodo = f"Gobernador {g['nombre']} ({g['aethyr']})"
    raiz = "BEYN_KRIMA" if g["cuadrante"]=="UMBRAL" else "YAMIN_DEXIOS"
    legiones = g["legiones"]
    entidades = legiones * ENTIDADES_POR_LEGION
    comandantes.append({"IdNodo":id_nodo,"Comandante":g["nombre"],"Faccion":"DERECHA (Control)","Raiz":raiz,"Rango":f"Gobernador {g['aethyr']}","Legiones":legiones,"Entidades":entidades,"Legiones_Str":f"{legiones} Legiones / {entidades:,} ent.","Funcion":g["funcion"],"OSINT":g["funcion"],"Ubicacion":g["jurisdiccion"],"Lat":g["lat"],"Lon":g["lon"],"Cuadrante":g["cuadrante"],"Aethyr":g["aethyr"]})
    rk = f"Gobernador {g['aethyr']}"
    if rk not in nodos_por_clase: nodos_por_clase[rk]=[]
    nodos_por_clase[rk].append(id_nodo)
    geo_map_data.append({"Comandante":id_nodo,"Nombre":g["nombre"],"Faccion":"DERECHA (Control)","Rango":f"Gobernador {g['aethyr']}","Lat":g["lat"],"Lon":g["lon"],"Ubicacion":g["jurisdiccion"],"Legiones":legiones,"Entidades":entidades,"Cuadrante":g["cuadrante"],"Fuente":"Liber Scientiae"})

# Vigilantes
id_vig = "Semyaza / Azazel (Vigilantes)"
comandantes.append({"IdNodo":id_vig,"Comandante":"Semyaza","Faccion":"IZQUIERDA (Caos)","Raiz":"YADA_GINOSKO","Rango":"Comandante","Legiones":200,"Entidades":200*ENTIDADES_POR_LEGION,"Legiones_Str":f"200 Caídos / {200*ENTIDADES_POR_LEGION:,} ent.","Funcion":"Rebelión e Hibridación Genética","OSINT":"Rebelión e Hibridación Genética","Ubicacion":"Monte Hermón (Levante)","Lat":33.4115,"Lon":35.8566,"Cuadrante":"Q4","Aethyr":"Libro de Enoc"})
geo_map_data.append({"Comandante":id_vig,"Nombre":"Semyaza","Faccion":"IZQUIERDA (Caos)","Rango":"Comandante","Lat":33.4115,"Lon":35.8566,"Ubicacion":"Monte Hermón (Levante)","Legiones":200,"Entidades":200*ENTIDADES_POR_LEGION,"Cuadrante":"Q4","Fuente":"Libro de Enoc"})

df_geo_map = pd.DataFrame(geo_map_data)
POB_MUNDIAL = 8_100_000_000

mapeo_infraestructura = {
    "BlackRock / Vanguard": "Rey Elemental Iczhihal",
    "Banco de Pagos Internacionales (BIS)": "Rey Elemental Iczhihal",
    "DARPA": "Rey Elemental Bataivah",
    "Palantir Technologies": "Gobernador Zinggenv (ZIM)",
    "CRISPR-Cas9 / Edición Genética": "Rey Asmoday",
    "Biología Sintética / ARNm": "Presidente Haagenti",
    "Neuralink": "Rey Bael",
    "OpenAI / Microsoft AI": "Rey Paimon"
}

# --- 7. GRAFO MAESTRO CON RESTAURACIÓN DE CITAS Y VERSÍCULOS ---
def generar_mapa_maestro(faccion, c_ling, c_geo, c_bio, textos_raw, activar_radar, limite_v=35):
    G = nx.Graph()
    color_faccion = "#e11d48" if "IZQUIERDA" in faccion else "#2563eb"
    G.add_node(str(faccion), size=70, color=color_faccion, title=f"🔥 EJE: {faccion}", font={"color":"white","size":24,"bold":True})
    
    if "DERECHA" in faccion:
        raices = {
            "YAMIN_DEXIOS": {"desc": "Yamin/Dexios — Autoridad y Ejecución", "color": "#3b82f6", "claves": ["YAMIN", "DEXIOS", "DERECHA", "CENTRAL", "CONTROL"]},
            "BEYN_KRIMA": {"desc": "Beyn/Krima — Límites y Separación", "color": "#60a5fa", "claves": ["BEYN", "KRIMA", "SEPARACION", "VIGILANCIA", "FILTRO", "LEY"]}
        }
    else:
        raices = {
            "SMOL_ARISTEROS": {"desc": "Smol/Aristeros — Disolución y Rebelión", "color": "#f43f5e", "claves": ["SMOL", "ARISTEROS", "IZQUIERDA", "CAOS", "DISOLUCION", "REBELION"]},
            "YADA_GINOSKO": {"desc": "Yada/Ginosko — Indistinción y Conocimiento Oculto", "color": "#fb7185", "claves": ["YADA", "GINOSKO", "ALTERACION", "HIBRIDACION", "MUTACION", "CONOCIMIENTO"]}
        }
        
    for r_id, info in raices.items():
        G.add_node(str(r_id), size=50, color=info["color"], title=f"Raíz Ontológica: {r_id}\n{info['desc']}\nBase: Jonás 4:11", font={"color":"white","size":18,"bold":True})
        G.add_edge(str(faccion), str(r_id), weight=5)
        
    comandantes_faccion = [c for c in comandantes if c["Faccion"] == faccion]
    
    # Nodos de radar interceptados
    operativos = []
    if activar_radar and comandantes_faccion:
        operativos = random.sample(comandantes_faccion, min(4, len(comandantes_faccion)))
        G.add_node("📡 RADAR OSINT ACTIVO", size=45, color="#22c55e", title="Señales activas interceptadas en tiempo real", font={"color":"#22c55e","size":16,"bold":True})
        G.add_edge(str(faccion), "📡 RADAR OSINT ACTIVO", weight=4)

    for cmd in comandantes_faccion:
        id_nodo = cmd["IdNodo"]
        esta = cmd in operativos
        cm = {"Q1":"#3b82f6","Q2":"#2563eb","Q3":"#be123c","Q4":"#e11d48","UMBRAL":"#0ea5e9"}
        color_nodo = "#22c55e" if esta else cm.get(cmd.get("Cuadrante","Q1"), "#475569")
        tamano_nodo = 30 if esta else 13
        
        G.add_node(id_nodo, size=tamano_nodo, color=color_nodo, title=f"👑 {id_nodo}\n📍 {cmd['Ubicacion']}\n⚔️ {cmd['Legiones_Str']}\n📜 {cmd['Funcion']}\n🧭 {CUADRANTES_PLANO.get(cmd.get('Cuadrante','Q1'),{}).get('nombre','—')}")
        G.add_edge(cmd["Raiz"], id_nodo, weight=1)
        if esta:
            G.add_edge("📡 RADAR OSINT ACTIVO", id_nodo, weight=3, color="#22c55e")
            
    # Interconexión entre pares del mismo rango
    for clase, nds in nodos_por_clase.items():
        nv = [n for n in nds if any(c["IdNodo"] == n and c["Faccion"] == faccion for c in comandantes)]
        if len(nv) > 1:
            for i in range(len(nv)):
                G.add_edge(nv[i], nv[(i+1)%len(nv)], weight=0.1, color="#1e293b")

    # Inyección de versículos masivos (Capa 0)
    if not c_ling.empty:
        for _, row in c_ling.head(limite_v).iterrows():
            if pd.isna(row.get('Libro')): continue
            nid = f"{row['Libro']} {row['Capitulo']}:{row['Versiculo']}"
            G.add_node(nid, size=13, color="#f8fafc", title=f"📖 {nid}\n{str(row.get('Traduccion','')).replace(chr(34),chr(39))}")
            conceptos = str(row.get('Conceptos_Matriz','')).upper()
            conectado = False
            for r_id, info in raices.items():
                if any(clave in conceptos for clave in info["claves"]):
                    G.add_edge(str(r_id), nid, weight=2)
                    conectado = True
                    break
            if not conectado:
                G.add_edge(str(faccion), nid, weight=1)

    # Inyección de Citas Textuales de Manuales Primarios
    if textos_raw:
        for nd, contenido in list(textos_raw.items())[:10]:
            for r_id, info in raices.items():
                for clave in info["claves"]:
                    if clave in contenido.upper():
                        G.add_node(f"Doc:{nd[:12]}", size=15, color="#d946ef", title=f"📜 {nd}\n{extraer_cita(contenido, clave)}")
                        G.add_edge(str(r_id), f"Doc:{nd[:12]}", weight=1)
                        break

    # Capas 2 y 3 (Infraestructura y Bio)
    def asociar_infra(df_c, col_nombre, col_desc, col_color, prefix):
        if not df_c.empty:
            for _, row in df_c.iterrows():
                if pd.isna(row.get(col_nombre)): continue
                nid = str(row[col_nombre]).strip()
                G.add_node(nid, size=24, color=col_color, title=f"🏢 {prefix}\n{str(row.get(col_desc,''))}")
                if nid in mapeo_infraestructura and any(c["IdNodo"] == mapeo_infraestructura[nid] and c["Faccion"] == faccion for c in comandantes_faccion):
                    G.add_edge(mapeo_infraestructura[nid], nid, weight=2)
                else:
                    G.add_edge(str(faccion), nid, weight=1)

    asociar_infra(c_geo, 'Entidad / Corporación', 'Mecanismo de Control', "#10b981", "CAPA 2 (Geo)")
    asociar_infra(c_bio, 'Avance / Plataforma', 'Mecanismo de Operación', "#f59e0b", "CAPA 3 (Bio)")

    net = Network(height="660px", width="100%", bgcolor="#0b0f19", font_color="white")
    net.from_nx(G)
    net.force_atlas_2based(gravity=-60, central_gravity=0.01, spring_length=140, spring_strength=0.05, damping=0.7)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        ruta_temp = f.name
        net.write_html(ruta_temp)
        
    return ruta_temp, [c["Comandante"] for c in operativos]

# --- 8. PLANO SEMÁNTICO DE JONÁS 4:11 ---
def generar_plano_semantico(faccion_filtro=None):
    coord_map = {"Q1": (0.5, 0.5), "Q2": (0.5, -0.5), "Q3": (-0.5, 0.5), "Q4": (-0.5, -0.5), "UMBRAL": (0.0, 0.0)}
    pts = []
    
    for g in GOBERNADORES_91:
        if faccion_filtro and faccion_filtro != "DERECHA (Control)": continue
        cx, cy = coord_map.get(g["cuadrante"], (0, 0))
        pts.append({"nombre": g["nombre"], "tipo": f"Gobernador {g['aethyr']}", "cuadrante": g["cuadrante"], "jurisdiccion": g["jurisdiccion"], "funcion": g["funcion"], "faccion": "DERECHA (Control)", "x": cx + (g["num"]%7 - 3)*0.07, "y": cy + (g["num"]%5 - 2)*0.07, "color": CUADRANTES_PLANO.get(g["cuadrante"],{}).get("color","#3b82f6"), "size": 8, "simbolo": "circle"})
        
    for cmd in comandantes:
        if cmd["Faccion"] != "IZQUIERDA (Caos)": continue
        if faccion_filtro and faccion_filtro != "IZQUIERDA (Caos)": continue
        cuad = cmd.get("Cuadrante", "Q4")
        cx, cy = coord_map.get(cuad, (-0.5, -0.5))
        pts.append({"nombre": cmd["Comandante"], "tipo": cmd["Rango"], "cuadrante": cuad, "jurisdiccion": cmd["Ubicacion"], "funcion": cmd["Funcion"], "faccion": "IZQUIERDA (Caos)", "x": cx + (hash(cmd["Comandante"])%7 - 3)*0.07, "y": cy + (hash(cmd["Comandante"])%5 - 2)*0.07, "color": CUADRANTES_PLANO.get(cuad,{}).get("color","#e11d48"), "size": 10 if cmd["Rango"]=="Rey" else 7, "simbolo": "diamond"})

    df_p = pd.DataFrame(pts)
    fig = go.Figure()
    
    # Cuadrantes
    fig.add_shape(type="rect", x0=0, x1=1.1, y0=0, y1=1.1, fillcolor="rgba(29,78,216,0.08)", line=dict(color="#1e293b"))
    fig.add_shape(type="rect", x0=0, x1=1.1, y0=-1.1, y1=0, fillcolor="rgba(37,99,235,0.08)", line=dict(color="#1e293b"))
    fig.add_shape(type="rect", x0=-1.1, x1=0, y0=0, y1=1.1, fillcolor="rgba(190,18,60,0.08)", line=dict(color="#1e293b"))
    fig.add_shape(type="rect", x0=-1.1, x1=0, y0=-1.1, y1=0, fillcolor="rgba(225,29,72,0.12)", line=dict(color="#1e293b"))
    
    # Ejes
    fig.add_shape(type="line", x0=-1.15, x1=1.15, y0=0, y1=0, line=dict(color="#334155", dash="dot"))
    fig.add_shape(type="line", x0=0, x1=0, y0=-1.15, y1=1.15, line=dict(color="#334155", dash="dot"))
    fig.add_shape(type="circle", x0=-0.15, x1=0.15, y0=-0.15, y1=0.15, fillcolor="rgba(14,165,233,0.15)", line=dict(color="#0ea5e9", dash="dash"))
    
    if not df_p.empty:
        for fac, grp in df_p.groupby("faccion"):
            fig.add_trace(go.Scatter(
                x=grp["x"], y=grp["y"], mode="markers", name=fac,
                marker=dict(size=grp["size"], color=grp["color"], symbol=grp["simbolo"], line=dict(color="#0b0f19", width=0.5)),
                text=grp["nombre"],
                customdata=grp[["cuadrante","jurisdiccion","funcion","tipo"]].values,
                hovertemplate="<b>%{text}</b><br>%{customdata[3]}<br>%{customdata[0]}<br>%{customdata[1]}<br>%{customdata[2]}<extra></extra>"
            ))
            
    fig.add_trace(go.Scatter(
        x=[-0.5], y=[-0.5], mode="markers+text", name="★ Jonás 4:11",
        marker=dict(size=18, color="#fbbf24", symbol="star", line=dict(color="#ffffff", width=1.5)),
        text=["יונה ד:יא"], textposition="top center", textfont=dict(color="#fbbf24", size=11),
        hovertemplate="<b>★ JONÁS 4:11</b><br>לֹא־יָדַע אִישׁ בֵּין־יְמִינוֹ לִשְׂמֹאלוֹ<extra></extra>"
    ))
    
    fig.update_layout(
        plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8",
        xaxis=dict(range=[-1.2, 1.2], showgrid=False, zeroline=False, fixedrange=True, showticklabels=False),
        yaxis=dict(range=[-1.2, 1.2], showgrid=False, zeroline=False, fixedrange=True, showticklabels=False),
        annotations=[
            dict(x=0.7, y=0.85, text="Q1 — CONTROL CON LÍMITES<br>YAMIN + BEYN", showarrow=False, font=dict(color="#3b82f6", size=10)),
            dict(x=0.7, y=-0.85, text="Q2 — AUTORIDAD / DISCERNIMIENTO<br>YAMIN + YADA", showarrow=False, font=dict(color="#2563eb", size=10)),
            dict(x=-0.7, y=0.85, text="Q3 — CAOS CONTENIDO<br>SMOL + BEYN", showarrow=False, font=dict(color="#be123c", size=10)),
            dict(x=-0.7, y=-0.85, text="Q4 — INDISTINCIÓN TOTAL<br>SMOL + YADA", showarrow=False, font=dict(color="#e11d48", size=10)),
            dict(x=0.0, y=-0.22, text="UMBRAL", showarrow=False, font=dict(color="#0ea5e9", size=9)),
            dict(x=1.1, y=0, text="YAMIN →", showarrow=False, font=dict(color="#3b82f6", size=10)),
            dict(x=-1.1, y=0, text="← SMOL", showarrow=False, font=dict(color="#e11d48", size=10)),
            dict(x=0, y=1.1, text="↑ BEYN", showarrow=False, font=dict(color="#60a5fa", size=10)),
            dict(x=0, y=-1.1, text="↓ YADA", showarrow=False, font=dict(color="#fb7185", size=10))
        ],
        margin=dict(l=15, r=15, t=35, b=25),
        height=550,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    return fig

# --- 9. MAPA TERRESTRE ---
def generar_mapa_cuadrantes_tierra():
    fig = go.Figure()
    cuad_geo = [
        dict(lat=[0,0,90,90,0],   lon=[0,180,180,0,0],   color="rgba(29,78,216,0.06)",  nombre="Q1 — Control con Límites (E/N)"),
        dict(lat=[0,0,-90,-90,0], lon=[0,180,180,0,0],   color="rgba(37,99,235,0.06)",  nombre="Q2 — Autoridad/Discernimiento (E/S)"),
        dict(lat=[0,0,90,90,0],   lon=[0,-180,-180,0,0], color="rgba(190,18,60,0.06)",  nombre="Q3 — Caos Contenido (W/N)"),
        dict(lat=[0,0,-90,-90,0], lon=[0,-180,-180,0,0], color="rgba(225,29,72,0.09)",  nombre="Q4 — Indistinción Total (W/S)"),
    ]
    for q in cuad_geo:
        fig.add_trace(go.Scattergeo(lat=q["lat"], lon=q["lon"], mode="lines", fill="toself", fillcolor=q["color"], line=dict(color="rgba(255,255,255,0.0)", width=0), name=q["nombre"], hoverinfo="name"))

    df_g = df_geo_map[df_geo_map["Lat"].notna() & (df_geo_map["Lat"] != 0)]
    color_map_cuad = {"Q1":"#3b82f6","Q2":"#2563eb","Q3":"#be123c","Q4":"#e11d48","UMBRAL":"#0ea5e9"}
    
    for faccion, group in df_g.groupby("Faccion"):
        simbolo = "circle" if "DERECHA" in faccion else "diamond"
        fig.add_trace(go.Scattergeo(
            lat=group["Lat"], lon=group["Lon"], mode="markers", name=faccion,
            marker=dict(
                size=group["Legiones"].apply(lambda x: max(5, min(22, x//10))).tolist(),
                color=[color_map_cuad.get(c, "#94a3b8") for c in group["Cuadrante"]],
                symbol=simbolo,
                line=dict(color="#0b0f19", width=0.5),
                opacity=0.85
            ),
            text=group["Nombre"],
            customdata=group[["Rango","Ubicacion","Legiones","Entidades","Cuadrante","Fuente"]].values,
            hovertemplate="<b>%{text}</b> (%{customdata[0]})<br>Ubicación: %{customdata[1]}<br>⚔️ Legiones: %{customdata[2]:,}<br>👁 Entidades: %{customdata[3]:,}<br>🧭 Cuadrante: %{customdata[4]}<extra></extra>"
        ))

    fig.update_geos(
        showcountries=True, countrycolor="#1e293b",
        showland=True, landcolor="#0f172a",
        showocean=True, oceancolor="#0b0f19",
        projection_type="natural earth",
        bgcolor="#0b0f19"
    )
    fig.update_layout(
        plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8",
        margin=dict(l=0, r=0, t=10, b=0), height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    return fig

# --- 10. RENDERIZADO DE PESTAÑAS ---
tab_core, tab_geo_d, tab_plano, tab_tierra, tab_ratio, tab_radar, tab_predict, tab_timeline, tab0, tab1, tab2, tab3, tab4, tab_arq = st.tabs([
    "🔄 Enjambre Jerárquico", "🗺️ Geo-Densidad", "🧭 Plano Semántico",
    "🌍 Cuadrantes Tierra", "⚖️ Ratio Legiones", "📡 Radar en Vivo",
    "🎯 Predictivo", "⏱️ Timeline",
    "📖 V0-Textos", "🔮 V1-Esotérico", "🌐 V2-Geo", "🧬 V3-Bio", "⏳ V4-Astro", "👥 Arquetipos"
])

# TAB 1: ENJAMBRE JERÁRQUICO
with tab_core:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Enjambre Total: 72 Goetia + 91 Gobernadores + 24 Ancianos + 4 Reyes Elementales")
        facción_maestra = st.radio("Ala de Comando:", ["DERECHA (Control)", "IZQUIERDA (Caos)"], horizontal=True)
    with col2:
        st.info("📡 **Radar OSINT**")
        activar_radar = st.checkbox("Activar radar en grafo", value=False)
        
    termino_ling = "Derecha" if "DERECHA" in facción_maestra else "Izquierda"
    c_ling = df_ling_masivo[df_ling_masivo["Conceptos_Matriz"].str.contains(termino_ling, na=False, case=False)] if not df_ling_masivo.empty else pd.DataFrame()
    c_geo_t = df_geo[df_geo["Facción Alineada"] == facción_maestra] if not df_geo.empty else pd.DataFrame()
    c_bio_t = df_bio[df_bio["Facción Alineada"] == facción_maestra] if not df_bio.empty else pd.DataFrame()
    
    ruta_grafo, interceptados = generar_mapa_maestro(facción_maestra, c_ling, c_geo_t, c_bio_t, textos_raw_eso, activar_radar, limite_nodos_texto)
    
    if activar_radar and interceptados:
        st.success(f"🟢 **Señales activas interceptadas en:** {', '.join(interceptados)}")
        
    with open(ruta_grafo, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=680)
    try:
        os.remove(ruta_grafo)
    except Exception:
        pass

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Raíces (Capa 0)", len(c_ling))
    m2.metric("Jerarcas", sum(1 for c in comandantes if c["Faccion"] == facción_maestra))
    m3.metric("Gobernadores Enoquianos", len(GOBERNADORES_91))
    m4.metric("Infraestructura Mapeada", len(c_geo_t) + len(c_bio_t))
    m5.metric("Ventanas Temporales", len(df_astro))

# TAB 2: GEO-DENSIDAD
with tab_geo_d:
    st.subheader("🗺️ Mapeo Geo-Densidad Histórico")
    df_z = df_geo_map.groupby(["Ubicacion","Lat","Lon","Faccion"]).agg({"Entidades":"sum","Legiones":"sum","Nombre":"count"}).reset_index().rename(columns={"Nombre":"Total_Jerarquicos"})
    df_z["Poblacion"] = df_z["Ubicacion"].map({"Britannia (Londres, UK)":9000000,"Sarmatia (Moscú, Rusia)":13000000,"Italia (Roma)":2800000,"Gallia (París, Francia)":11000000,"Mesopotamia (Damasco, Siria)":2000000,"Bactriana (Nueva Delhi, India)":32000000,"Babilonia (Hillah, Irak)":500000,"Persia (Teherán, Irán)":9000000,"Egipto (El Cairo)":22000000,"Fenicia / Sidón (Líbano)":200000,"Desierto de Arabia (Riad, AS)":7500000,"Sodoma (Mar Muerto, Jordania)":100000,"Monte Hermón (Levante)":50000}).fillna(1000000)
    df_z["Ratio"] = df_z.apply(lambda r: round(r["Poblacion"]/r["Entidades"], 2) if r["Entidades"]>0 else 0, axis=1)
    df_z["Hover"] = df_z.apply(lambda r: f"<b>{r['Ubicacion']}</b><br>Jerarcas: {r['Total_Jerarquicos']}<br>Legiones: {r['Legiones']:,}<br>Entidades: {r['Entidades']:,}<br>Población: {r['Poblacion']:,}<br>Densidad: 1 ent. cada {r['Ratio']} hab.", axis=1)
    fig_map = px.scatter_geo(df_z, lat="Lat", lon="Lon", size="Entidades", color="Faccion", hover_name="Ubicacion", custom_data=["Hover"], projection="natural earth", color_discrete_map={"DERECHA (Control)":"#3b82f6","IZQUIERDA (Caos)":"#f43f5e"})
    fig_map.update_traces(hovertemplate="%{customdata[0]}")
    fig_map.update_geos(showcountries=True, countrycolor="#334155", showland=True, landcolor="#0f172a", showocean=True, oceancolor="#0b0f19")
    fig_map.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8", margin=dict(l=0, r=0, t=10, b=0), height=500, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
    st.plotly_chart(fig_map, use_container_width=True, config=PLOTLY_CONFIG)

# TAB 3: PLANO SEMÁNTICO
with tab_plano:
    st.subheader("🧭 Plano Semántico — Fundamento Jonás 4:11")
    
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        st.markdown("""
        **VÉRTICE GENERADOR:** `יונה ד:יא` (*Yona 4:11*)  
        > *«¿Y no he de apiadarme yo de Nínive, la gran ciudad, donde hay más de ciento veinte mil personas que **no saben discernir entre su derecha y su izquierda**...?»*
        
        * **Eje Horizontal (Control vs Disolución):**
          * **`יָמִין` (Yamin / Dexios):** Mano derecha, orden jerárquico, legitimidad, autoridad constituida.
          * **`שְׂמֹאל` (Smol / Aristeros):** Mano izquierda, dispersión, rebelión, entropía, disolución de formas.
        * **Eje Vertical (Discriminación vs Fusión):**
          * **`בֵּין` (Beyn / Krima):** Frontera, juicio divisorio, discernir, separación taxonómica.
          * **`יָדַע` (Yada / Ginosko):** Conocimiento por asimilación, hibridación, disolución del umbral de identidad.
        """)
    with col_p2:
        filtro_fac = st.selectbox("Filtrar Cuadrante por Facción:", ["Todas", "DERECHA (Control)", "IZQUIERDA (Caos)"])
        filtro = None if filtro_fac == "Todas" else filtro_fac
        
    st.plotly_chart(generar_plano_semantico(filtro), use_container_width=True, config=PLOTLY_CONFIG)
    
    st.markdown("---")
    cols_c = st.columns(5)
    for i, (k, v) in enumerate(CUADRANTES_PLANO.items()):
        with cols_c[i]:
            st.markdown(f"<div style='background:#0f172a;border:1px solid {v['color']};border-radius:8px;padding:10px'><b style='color:{v['color']}'>{k}</b><br><small style='color:#e2e8f0'><b>{v['nombre']}</b></small><br><small style='color:#94a3b8'>{v['descripcion']}</small></div>", unsafe_allow_html=True)

# TAB 4: CUADRANTES TIERRA
with tab_tierra:
    st.subheader("🌍 Cuadrantes Semánticos Proyectados sobre la Tierra")
    st.markdown("""
    * **Cuadrante Q1 (Este/Norte):** Control con Límites (*Yamin + Beyn*) — Eje Euroasiático y Mesopotámico.
    * **Cuadrante Q2 (Este/Sur):** Autoridad por Discernimiento (*Yamin + Yada*) — África y Subcontinente Índico.
    * **Cuadrante Q3 (Oeste/Norte):** Caos Contenido (*Smol + Beyn*) — Complejo Atlántico Norte.
    * **Cuadrante Q4 (Oeste/Sur):** Indistinción Total (*Smol + Yada*) — Espacio de hibridación radical.
    """)
    st.plotly_chart(generar_mapa_cuadrantes_tierra(), use_container_width=True, config=PLOTLY_CONFIG)

# TAB 5: RATIO LEGIONES (CORREGIDO Y EXPLICADO)
with tab_ratio:
    st.subheader("⚖️ Conteo de Legiones y Ratio por Habitante")
    st.caption(f"Base ontológica: 1 legión = {ENTIDADES_POR_LEGION:,} entidades. Población humana mundial estimada: {POB_MUNDIAL:,}")

    entidades_izq = df_geo_map[df_geo_map["Faccion"] == "IZQUIERDA (Caos)"]["Entidades"].sum()
    legiones_izq  = df_geo_map[df_geo_map["Faccion"] == "IZQUIERDA (Caos)"]["Legiones"].sum()
    entidades_der = df_geo_map[df_geo_map["Faccion"] == "DERECHA (Control)"]["Entidades"].sum()
    legiones_der  = df_geo_map[df_geo_map["Faccion"] == "DERECHA (Control)"]["Legiones"].sum()
    total_entidades = entidades_izq + entidades_der
    total_legiones  = legiones_izq + legiones_der

    ratio_global = total_entidades / POB_MUNDIAL
    humanos_por_entidad_total = POB_MUNDIAL / total_entidades if total_entidades > 0 else 0
    humanos_por_entidad_izq = POB_MUNDIAL / entidades_izq if entidades_izq > 0 else 0
    humanos_por_entidad_der = POB_MUNDIAL / entidades_der if entidades_der > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Legiones Totales", f"{total_legiones:,}")
        st.caption(f"IZQ: {legiones_izq:,} | DER: {legiones_der:,}")
    with c2:
        st.metric("Entidades Totales", f"{total_entidades:,}")
        st.caption(f"Base: {total_legiones:,} × {ENTIDADES_POR_LEGION:,}")
    with c3:
        st.metric("Densidad Global", f"{ratio_global:.4f} ent./hab.")
        st.caption(f"IZQ: {entidades_izq/POB_MUNDIAL:.4f} | DER: {entidades_der/POB_MUNDIAL:.4f}")
    with c4:
        st.metric("Ratio Poblacional", f"1 ent. / {round(humanos_por_entidad_total)} hab.")
        st.caption("Frecuencia demográfica humana")

    st.markdown("---")

    with st.expander("📚 Explicación Matemática y Diferenciación Faccional", expanded=True):
        st.markdown(f"""
        ### ¿Por qué esta cantidad de entidades y qué significa el ratio?
        
        1. **La constante de legión:** En la tradición clásica y textual, una legión jerárquica comprende **6.666 entidades**.
        2. **Cómputo por facciones:**
           * **Ala Izquierda (Caos / Entropía / Hibridación):** Agrupa a los 72 gobernantes de la Goetia y a los líderes Vigilantes (Monte Hermón). Totalizan **{legiones_izq:,} legiones**, lo que equivale a **{entidades_izq:,} entidades**.
           * **Ala Derecha (Control / Delimitación / Jerarquía):** Agrupa a los 91 Gobernadores Enoquianos, 24 Ancianos y 4 Reyes Elementales. Totalizan **{legiones_der:,} legiones**, lo que equivale a **{entidades_der:,} entidades**.
        3. **Interpretación del Ratio:**
           * **Presencia Directa:** Hay **`{ratio_global:.4f}` entidades por cada ser humano** en el planeta.
           * **Dispersión Poblacional:** Existe **1 entidad de control (Ala Derecha) por cada {round(humanos_por_entidad_der):,} seres humanos**, y **1 entidad de disolución (Ala Izquierda) por cada {round(humanos_por_entidad_izq):,} seres humanos**. En conjunto, existe **1 entidad por cada {round(humanos_por_entidad_total)} habitantes**.
        """)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Distribución por Ala")
        df_fac = pd.DataFrame([
            {"Facción": "DERECHA (Control)", "Legiones": f"{legiones_der:,}", "Entidades": f"{entidades_der:,}", "Ratio ent./hab.": f"{entidades_der/POB_MUNDIAL:.5f}", "Proporción": f"1 ent. cada {round(humanos_por_entidad_der)} hab."},
            {"Facción": "IZQUIERDA (Caos)", "Legiones": f"{legiones_izq:,}", "Entidades": f"{entidades_izq:,}", "Ratio ent./hab.": f"{entidades_izq/POB_MUNDIAL:.5f}", "Proporción": f"1 ent. cada {round(humanos_por_entidad_izq)} hab."}
        ])
        st.dataframe(df_fac, use_container_width=True, hide_index=True)
    with col_b:
        st.markdown("### Por Fuente Canónica")
        by_fuente = df_geo_map.groupby(["Fuente","Faccion"]).agg({"Entidades":"sum","Legiones":"sum"}).reset_index()
        by_fuente["Ratio"] = by_fuente["Entidades"].apply(lambda x: f"{x/POB_MUNDIAL:.5f}")
        st.dataframe(by_fuente, use_container_width=True, hide_index=True)

    st.markdown("---")
    fig_tree = px.treemap(
        df_geo_map, path=["Faccion", "Fuente", "Rango"], values="Entidades",
        color="Faccion", color_discrete_map={"IZQUIERDA (Caos)": "#e11d48", "DERECHA (Control)": "#2563eb"}
    )
    fig_tree.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8", margin=dict(l=0, r=0, t=20, b=0), height=460)
    st.plotly_chart(fig_tree, use_container_width=True, config=PLOTLY_CONFIG)

# TAB 6: RADAR EN VIVO
with tab_radar:
    st.subheader("📡 Radar en Vivo — Movimientos de Entidades y Señales")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1: faccion_radar = st.selectbox("Facción:", ["Todas", "DERECHA (Control)", "IZQUIERDA (Caos)"], key="rad_fac")
    with col_r2: fuente_radar = st.selectbox("Fuente:", ["Todas", "Goetia", "Gobernadores Enoquianos", "Reyes Elementales", "Vigilantes"], key="rad_src")
    with col_r3: cuad_radar = st.selectbox("Cuadrante:", ["Todos", "Q1", "Q2", "Q3", "Q4", "UMBRAL"], key="rad_cuad")

    entidades_radar = []
    for cmd in comandantes:
        fac_ok = faccion_radar == "Todas" or cmd["Faccion"] == faccion_radar
        cuad_ok = cuad_radar == "Todos" or cmd.get("Cuadrante", "") == cuad_radar
        src_ok = True
        if fuente_radar == "Goetia": src_ok = cmd.get("Aethyr") == "Ars Goetia"
        elif fuente_radar == "Gobernadores Enoquianos": src_ok = "Gobernador" in cmd.get("Rango", "")
        elif fuente_radar == "Reyes Elementales": src_ok = cmd.get("Rango", "").startswith("Rey Elemental")
        elif fuente_radar == "Vigilantes": src_ok = cmd.get("Aethyr") == "Libro de Enoc"
        if fac_ok and cuad_ok and src_ok: entidades_radar.append(cmd)

    entidades_radar = entidades_radar[:15]
    if not entidades_radar:
        st.info("No hay entidades que coincidan con el filtro.")
    else:
        st.markdown(f"Rastreando **{len(entidades_radar)}** jerarcas estratégicos.")
        if st.button("🔍 Escanear Señales en Tiempo Real", type="primary"):
            prog = st.progress(0); res = {}
            for i, ent in enumerate(entidades_radar):
                nots = buscar_noticias_entidad(ent["Funcion"], ent["Comandante"], NEWSAPI_KEY)
                if nots: res[ent["IdNodo"]] = {"entidad": ent, "noticias": nots}
                prog.progress((i+1)/len(entidades_radar))
            prog.empty()
            
            if not res:
                st.warning("No se detectaron señales abiertas en los feeds en este instante.")
            else:
                st.success(f"✅ {sum(len(v['noticias']) for v in res.values())} señales detectadas en {len(res)} entidades.")
                for id_nodo, data in res.items():
                    ent = data["entidad"]; nots = data["noticias"]
                    col_ent = CUADRANTES_PLANO.get(ent.get("Cuadrante","Q1"),{}).get("color","#94a3b8")
                    with st.expander(f"{ent['IdNodo']} — {len(nots)} señales activas", expanded=False):
                        for n in nots:
                            st.markdown(f"""
                            <div style='background:#0f172a;border-left:3px solid {col_ent};padding:10px 14px;margin:6px 0;border-radius:0 8px 8px 0'>
                                <div style='display:flex;justify-content:space-between'>
                                    <small style='color:#64748b'>{n.get('fuente','—')}</small>
                                    <small style='color:#64748b'>{n.get('fecha','')}</small>
                                </div>
                                <b style='color:#e2e8f0;font-size:13px'>{n.get('titulo','')}</b><br>
                                <small style='color:#94a3b8'>{str(n.get('descripcion',''))[:180]}...</small><br>
                                <a href='{n.get('url','#')}' target='_blank' style='color:{col_ent};font-size:12px;text-decoration:none'>→ Ver despacho</a>
                            </div>
                            """, unsafe_allow_html=True)

# TAB 7: PREDICTIVO
with tab_predict:
    st.subheader("🎯 Algoritmo de Convergencia Vectorial")
    cp1, cp2, cp3 = st.columns(3)
    og = df_geo['Entidad / Corporación'].dropna().tolist() if not df_geo.empty else ["Sin datos"]
    ob = df_bio['Avance / Plataforma'].dropna().tolist() if not df_bio.empty else ["Sin datos"]
    oa = df_astro['Ciclo / Marcador Celeste'].dropna().tolist() if not df_astro.empty else ["Sin datos"]
    with cp1: vg = st.selectbox("1. Entidad Geopolítica:", og)
    with cp2: vb = st.selectbox("2. Avance Biotecnológico:", ob)
    with cp3: va = st.selectbox("3. Ventana Temporal:", oa)
    
    if st.button("Analizar Convergencia", type="primary"):
        fg = df_geo[df_geo['Entidad / Corporación'] == vg]['Facción Alineada'].values[0] if vg in df_geo['Entidad / Corporación'].values else "Desconocida"
        fb = df_bio[df_bio['Avance / Plataforma'] == vb]['Facción Alineada'].values[0] if vb in df_bio['Avance / Plataforma'].values else "Desconocida"
        if fg == fb:
            st.progress(0.85)
            st.markdown(f"<h3 style='color:#ef4444'>⚠️ ALTA CONVERGENCIA SISTÉMICA (85%): {vg} y {vb} responden a la misma agenda ({fg}).</h3>", unsafe_allow_html=True)
        else:
            st.progress(0.40)
            st.markdown(f"<h3 style='color:#f59e0b'>⚡ FRICCIÓN ESTRUCTURAL (40%): {vg} ({fg}) colisiona tácticamente con {vb} ({fb}).</h3>", unsafe_allow_html=True)

# TAB 8: TIMELINE
with tab_timeline:
    st.subheader("⏱️ Línea de Tiempo Astro-Estructural")
    if 'Inicio' in df_astro.columns and 'Fin' in df_astro.columns:
        df_tl = df_astro.dropna(subset=['Inicio','Fin'])
        if not df_tl.empty:
            fig_tl = px.timeline(df_tl, x_start="Inicio", x_end="Fin", y="Ciclo / Marcador Celeste", color="Facción Alineada", color_discrete_map={"DERECHA (Control)":"#3b82f6","IZQUIERDA (Caos)":"#f43f5e","Ambas / Reloj":"#0ea5e9"})
            fig_tl.update_yaxes(autorange="reversed")
            fig_tl.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8", margin=dict(l=0, r=0, t=10, b=0), height=420)
            st.plotly_chart(fig_tl, use_container_width=True, config=PLOTLY_CONFIG)

# TABLAS DE VECTORES
with tab0: st.dataframe(df_ling_masivo, use_container_width=True, hide_index=True)
with tab1:
    st.dataframe(df_eso_base, use_container_width=True, hide_index=True)
    if textos_raw_eso:
        st.markdown("---"); st.subheader("📜 Fuentes Primarias Transcritas")
        sel = st.selectbox("Documento:", list(textos_raw_eso.keys()))
        st.markdown(f"""<div style="height:380px;overflow-y:auto;background:#0f172a;padding:16px;border:1px solid #334155;border-radius:8px;color:#38bdf8;font-family:'Courier New',monospace;white-space:pre-wrap">{html.escape(textos_raw_eso[sel])}</div>""", unsafe_allow_html=True)
with tab2: st.dataframe(df_geo, use_container_width=True, hide_index=True)
with tab3: st.dataframe(df_bio, use_container_width=True, hide_index=True)
with tab4: st.dataframe(df_astro, use_container_width=True, hide_index=True)
with tab_arq: st.dataframe(df_arquetipos, use_container_width=True, hide_index=True)