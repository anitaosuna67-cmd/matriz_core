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

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS RESPONSIVE ---
st.set_page_config(
    page_title="Matriz Core - Intelligence Terminal",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main { background-color: #0b0f19; }
    h1, h2, h3 { color: #e2e8f0 !important; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-size: 0.9rem; }
    .stTabs [aria-selected="true"] { color: #38bdf8 !important; border-bottom-color: #38bdf8 !important; }
    div[data-testid="stMetricValue"] { color: #38bdf8 !important; font-size: 1.6rem !important; }
    .css-1d391kg { background-color: #0f172a; }
    
    /* Optimización táctil y mobile */
    @media (max-width: 768px) {
        div[data-testid="stMetricValue"] { font-size: 1.25rem !important; }
        .stTabs [data-baseweb="tab"] { padding: 4px 8px !important; font-size: 0.78rem; }
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
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=50)
    st.title("Matriz Core")
    st.caption("Terminal OSINT & Ontología de Poder")
    
    with st.expander("🧭 Arquitectura del Pipeline", expanded=False):
        st.markdown("""
        * **Capa 0 (Textual):** Semántica de raíces bíblicas (Yamin/Smol/Beyn/Yada).
        * **Capa 1 (Topología):** Gobernadores Enoquianos, Goetia y distribución cartesiana.
        * **Capas 2-3 (Infraestructura):** Finanzas, complejos militares y biotecnología.
        * **Capa 4 (Dinámica):** Marcadores astro-temporales y satélites OSINT.
        """)
    
    st.markdown("---")
    st.subheader("⚙️ Configuración")
    input_api_key = st.text_input("NewsAPI Key (Opcional):", value=os.getenv("NEWSAPI_KEY", ""), type="password")
    limite_nodos_texto = st.slider("Límite de nodos textuales:", 10, 80, 25)

NEWSAPI_KEY = input_api_key.strip() if input_api_key else os.getenv("NEWSAPI_KEY", "")

# Título conciso
st.title("🔮 CORE MATRIX // INTEL TERMINAL")
st.caption("Monitoreo de Fuerzas Jerárquicas, Proyección Geoespacial y Convergencia de Vectores")

# --- 4. CARGA DE DATOS CON FALLBACK ROBUSTO ---
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

df_ling_masivo   = cargar_textos_masivos()
df_eso_base      = cargar_excel(ruta_esoterico, "Datos Esotéricos")
df_geo_base      = cargar_excel(ruta_geopolitico, "Estructuras de Control")
df_bio_base      = cargar_excel(ruta_biotecnologico, "Alteraciones Biológicas")
df_astro_base    = cargar_excel(ruta_astro, "Reloj del Sistema")
df_arquetipos    = cargar_excel(ruta_base, "Arquetipos de Facciones")
textos_raw_eso   = cargar_manuales_raw()

# Enriquecimiento de Capa 2 (Geopolítica / Corporativa)
infraestructura_geopolitica_extra = [
    {"Entidad / Corporación": "BlackRock / Vanguard", "Tipo": "Gestora Financiera Global", "Mecanismo de Control": "Monopolio accionario de activos estratégicos globales", "Facción Alineada": "DERECHA (Control)"},
    {"Entidad / Corporación": "Banco de Pagos Internacionales (BIS)", "Tipo": "Banca Central de Bancos Centrales", "Mecanismo de Control": "Emisión crediticia soberana y protocolos monetarios", "Facción Alineada": "DERECHA (Control)"},
    {"Entidad / Corporación": "DARPA", "Tipo": "Agencia Militar de Proyectos Avanzados", "Mecanismo de Control": "Innovación bélica autónoma y cibernética de vigilancia", "Facción Alineada": "DERECHA (Control)"},
    {"Entidad / Corporación": "Palantir Technologies", "Tipo": "Inteligencia Predictiva Militar", "Mecanismo de Control": "Minería masiva de datos y focalización de blancos", "Facción Alineada": "DERECHA (Control)"},
    {"Entidad / Corporación": "Foro Económico Mundial (WEF)", "Tipo": "Gobernanza Público-Privada", "Mecanismo de Control": "Estandarización de métricas ESG y pautas transhumanistas", "Facción Alineada": "DERECHA (Control)"},
    {"Entidad / Corporación": "GCHQ / NSA (Five Eyes)", "Tipo": "Aparato de Señales e Inteligencia", "Mecanismo de Control": "Interceptación global de telecomunicaciones", "Facción Alineada": "DERECHA (Control)"},
    {"Entidad / Corporación": "OpenAI / Microsoft AI", "Tipo": "Monopolio de Inteligencia Artificial", "Mecanismo de Control": "Moldeo algorítmico cognitivo y automatización sintética", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Entidad / Corporación": "Neuralink", "Tipo": "Interfaz Cerebro-Máquina", "Mecanismo de Control": "Integración bio-digital directa y disolución de privacidad neural", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Entidad / Corporación": "Plataformas ARNm / Pfizer / Moderna", "Tipo": "Biotecnología Génica", "Mecanismo de Control": "Reprogramación celular y respuesta molecular dirigida", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Entidad / Corporación": "TSMC (Semiconductores Taiwán)", "Tipo": "Monopolio de Silicio", "Mecanismo de Control": "Chokepoint físico para la infraestructura global de cómputo", "Facción Alineada": "DERECHA (Control)"}
]
df_geo = pd.concat([df_geo_base, pd.DataFrame(infraestructura_geopolitica_extra)], ignore_index=True) if not df_geo_base.empty else pd.DataFrame(infraestructura_geopolitica_extra)

bio_extra = [
    {"Avance / Plataforma": "CRISPR-Cas9 / Edición Genética", "Mecanismo de Operación": "Corte de precisión y recombinación de ADN", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Avance / Plataforma": "Quimeras Humano-Animal", "Mecanismo de Operación": "Hibridación interespecie celular", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Avance / Plataforma": "Biología Sintética / ARNm", "Mecanismo de Operación": "Instrucción transcriptómica sintética", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Avance / Plataforma": "Identificación Biométrica Digital", "Mecanismo de Operación": "Trazabilidad de individuos por parámetros físicos", "Facción Alineada": "DERECHA (Control)"}
]
df_bio = pd.concat([df_bio_base, pd.DataFrame(bio_extra)], ignore_index=True) if not df_bio_base.empty else pd.DataFrame(bio_extra)

nuevos_ciclos_astro = [
    {"Ciclo / Marcador Celeste": "Conjunción Júpiter-Saturno", "Inicio": "2020-12-21", "Fin": "2040-10-31", "Impacto Estructural": "Mutación a Aire. Digitalización del control.", "Facción Alineada": "DERECHA (Control)"},
    {"Ciclo / Marcador Celeste": "Tránsito de Urano en Tauro", "Inicio": "2018-05-15", "Fin": "2026-04-26", "Impacto Estructural": "Disrupción radical de la biología y agricultura.", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Ciclo / Marcador Celeste": "Entrada de Plutón en Acuario", "Inicio": "2023-03-23", "Fin": "2043-03-08", "Impacto Estructural": "Revolución transhumanista, IA general.", "Facción Alineada": "IZQUIERDA (Caos)"},
    {"Ciclo / Marcador Celeste": "Conjunción Saturno-Plutón", "Inicio": "2020-01-12", "Fin": "2021-12-31", "Impacto Estructural": "Contracción extrema y fronteras cerradas.", "Facción Alineada": "DERECHA (Control)"},
    {"Ciclo / Marcador Celeste": "Retorno de Plutón (USA)", "Inicio": "2022-02-20", "Fin": "2024-11-19", "Impacto Estructural": "Fractura interna de los imperios occidentales.", "Facción Alineada": "Ambas / Reloj"}
]
df_astro = pd.concat([df_astro_base, pd.DataFrame(nuevos_ciclos_astro)], ignore_index=True) if not df_astro_base.empty else pd.DataFrame(nuevos_ciclos_astro)

# --- 5. MOTOR OSINT CON RECEPTOR DINÁMICO DE API KEY ---
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
    "Espionaje": ["cyber espionage intelligence", "surveillance state NSA"],
    "default": ["geopolitics power elite", "defense intelligence operations"]
}

@st.cache_data(ttl=3600)
def buscar_noticias_entidad(funcion: str, nombre: str, api_key_activa: str = "") -> list:
    keywords = KEYWORDS_REALES.get(funcion, KEYWORDS_REALES["default"])
    query = " OR ".join(f'"{k}"' for k in keywords[:2])
    
    if api_key_activa:
        try:
            resp = requests.get("https://newsapi.org/v2/everything", params={
                "q": query, "language": "en", "sortBy": "publishedAt", "pageSize": 5,
                "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"), "apiKey": api_key_activa
            }, timeout=6)
            data = resp.json()
            if data.get("status") == "ok" and data.get("articles"):
                return [{
                    "titulo": a.get("title", ""),
                    "descripcion": a.get("description", ""),
                    "url": a.get("url", "#"),
                    "fuente": a.get("source", {}).get("name", "NewsAPI"),
                    "fecha": str(a.get("publishedAt", ""))[:10]
                } for a in data["articles"][:5]]
        except Exception:
            pass
            
    # Fallback seguro por RSS
    try:
        kw = keywords[0] if keywords else "geopolitics"
        rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(kw)}&hl=en&gl=US&ceid=US:en"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
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

# --- 6. TOPOLOGÍA ONTOLÓGICA Y ENTIDADES ---
CUADRANTES_PLANO = {
    "Q1": {"nombre": "Control con Límites", "eje_x": 1, "eje_y": 1, "faccion": "DERECHA (Control)", "color": "#1d4ed8", "descripcion": "Autoridad ejercida por separación y límites formales."},
    "Q2": {"nombre": "Autoridad por Discernimiento", "eje_x": 1, "eje_y": -1, "faccion": "DERECHA (Control)", "color": "#2563eb", "descripcion": "Sabiduría y discernimiento operativo."},
    "Q3": {"nombre": "Caos Contenido", "eje_x": -1, "eje_y": 1, "faccion": "IZQUIERDA (Caos)", "color": "#be123c", "descripcion": "Transgresión consciente de fronteras."},
    "Q4": {"nombre": "Indistinción Total", "eje_x": -1, "eje_y": -1, "faccion": "IZQUIERDA (Caos)", "color": "#e11d48", "descripcion": "Colapso del discernimiento. Hibridación pura (Jonás 4:11)."},
    "UMBRAL": {"nombre": "Zona de Frontera", "eje_x": 0, "eje_y": 0, "faccion": "Ambas / Umbral", "color": "#0ea5e9", "descripcion": "Espacio liminal intermedio."}
}

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
    {"nombre":"Tiarpax","aethyr":"DES","num":15,"jurisdiccion":"Hispania / Iberia","funcion":"Expansión ordenada de jurisdicción territorial","cuadrante":"Q1","lat":40.4,"lon":-3.7,"legiones":30},
    {"nombre":"Saxtomp","aethyr":"VTI","num":16,"jurisdiccion":"Britania / Stonehenge","funcion":"Calibración de ciclos temporales y astronómicos","cuadrante":"Q2","lat":51.1,"lon":-1.8,"legiones":30},
    {"nombre":"Genadol","aethyr":"LIN","num":26,"jurisdiccion":"Roma / Italia","funcion":"Derecho institucional, jurisprudencia y precedente","cuadrante":"Q1","lat":41.9,"lon":12.4,"legiones":30},
    {"nombre":"Aspiaon","aethyr":"LIN","num":27,"jurisdiccion":"Judea / Jerusalén","funcion":"Ley sagrada, regulación de lo puro e impuro","cuadrante":"Q1","lat":31.7,"lon":35.2,"legiones":30},
    {"nombre":"Vivipos","aethyr":"POP","num":35,"jurisdiccion":"China / Valle del Amarillo","funcion":"Censos, clasificación y registro de poblaciones","cuadrante":"Q1","lat":34.7,"lon":113.6,"legiones":30},
    {"nombre":"Gebabal","aethyr":"ZIM","num":52,"jurisdiccion":"Venecia / Banca Medieval","funcion":"Creación y regulación de sistemas de valor","cuadrante":"Q1","lat":45.4,"lon":12.3,"legiones":30},
    {"nombre":"Zinggenv","aethyr":"ZIM","num":54,"jurisdiccion":"Londres / City","funcion":"Banca central y monopolio de la emisión","cuadrante":"Q1","lat":51.5,"lon":-0.08,"legiones":30},
    {"nombre":"Lexarph","aethyr":"ZAX","num":61,"jurisdiccion":"El Abismo","funcion":"Guardián del umbral entre el ser y el no-ser","cuadrante":"UMBRAL","lat":0.0,"lon":0.0,"legiones":30},
    {"nombre":"Sodalzt","aethyr":"LIT","num":78,"jurisdiccion":"Silicon Valley / Digital","funcion":"Algoritmos de filtrado y curación de realidad","cuadrante":"Q2","lat":37.3,"lon":-122.0,"legiones":30},
    {"nombre":"Pothnirv","aethyr":"PAZ","num":81,"jurisdiccion":"Naciones Unidas / NY","funcion":"Multilateralismo como mecanismo de contención","cuadrante":"Q1","lat":40.7,"lon":-74.0,"legiones":30},
    {"nombre":"Lrasd","aethyr":"LIL","num":91,"jurisdiccion":"LIL / Cierre","funcion":"El sellado — cierre del ciclo completo del sistema","cuadrante":"Q1","lat":57.0,"lon":35.0,"legiones":30}
]

goetia_72 = [
    ("Bael","Rey",66,"Invisibilidad"),("Agares","Duque",31,"Terremotos"),("Vassago","Príncipe",26,"Secretos"),("Samigina","Marqués",30,"Nigromancia"),("Marbas","Presidente",36,"Enfermedades"),("Valefor","Duque",10,"Robo"),("Amon","Marqués",40,"Ira"),("Barbatos","Duque",30,"Tesoros"),("Paimon","Rey",200,"Manipulación"),("Buer","Presidente",50,"Biología"),
    ("Gusion","Duque",40,"Diplomacia"),("Sitri","Príncipe",60,"Lujuria"),("Beleth","Rey",85,"Pasiones"),("Leraje","Marqués",30,"Guerra"),("Eligos","Duque",60,"Milicia"),("Zepar","Duque",26,"Mutación"),("Botis","Presidente",60,"Facciones"),("Purson","Rey",22,"Materialismo"),("Asmoday","Rey",72,"Destrucción Genética"),("Belial","Rey",80,"Favores políticos")
]

ENTIDADES_POR_LEGION = 6666
comandantes = []
nodos_por_clase = {}
geo_map_data = []
random.seed(42)

nodos_goetia = [("Babilonia (Hillah, Irak)",32.5363,44.4208),("Persia (Teherán, Irán)",35.6892,51.3890),("Egipto (El Cairo)",30.0444,31.2357),("Sodoma (Mar Muerto)",31.3333,35.5000)]
nodos_enoc   = [("Britannia (Londres, UK)",51.5074,-0.1278),("Italia (Roma)",41.9028,12.4964),("Gallia (París, Francia)",48.8566,2.3522),("Nueva York / ONU",40.7128,-74.0060)]

# Carga Goetia
for nombre, rango, legiones, funcion in goetia_72:
    raiz = "SMOL_ARISTEROS" if rango in ["Rey","Marqués"] else "YADA_GINOSKO"
    id_nodo = f"{rango} {nombre}"
    lugar = random.choice(nodos_goetia)
    cuad = "Q4" if rango in ["Rey","Marqués"] else "Q3"
    entidades = legiones * ENTIDADES_POR_LEGION
    item = {"IdNodo":id_nodo,"Comandante":nombre,"Faccion":"IZQUIERDA (Caos)","Raiz":raiz,"Rango":rango,"Legiones":legiones,"Entidades":entidades,"Legiones_Str":f"{legiones} Legiones / {entidades:,} ent.","Funcion":funcion,"OSINT":funcion,"Ubicacion":lugar[0],"Lat":lugar[1],"Lon":lugar[2],"Cuadrante":cuad,"Aethyr":"Ars Goetia"}
    comandantes.append(item)
    geo_map_data.append({"Comandante":id_nodo,"Nombre":nombre,"Faccion":"IZQUIERDA (Caos)","Rango":rango,"Lat":lugar[1],"Lon":lugar[2],"Ubicacion":lugar[0],"Legiones":legiones,"Entidades":entidades,"Cuadrante":cuad,"Fuente":"Ars Goetia"})

# Reyes Elementales
reyes_enoc = [("Bataivah","Rey Elemental","Aire",100),("Raagiosl","Rey Elemental","Agua",100),("Iczhihal","Rey Elemental","Tierra",100),("Edaiel","Rey Elemental","Fuego",100)]
for nombre, rango, dominio, legiones in reyes_enoc:
    id_nodo = f"{rango} {nombre}"
    lugar = random.choice(nodos_enoc)
    entidades = legiones * ENTIDADES_POR_LEGION
    fn = f"Gobierno del {dominio}"
    comandantes.append({"IdNodo":id_nodo,"Comandante":nombre,"Faccion":"DERECHA (Control)","Raiz":"YAMIN_DEXIOS","Rango":rango,"Legiones":legiones,"Entidades":entidades,"Legiones_Str":f"{legiones} Legiones / {entidades:,} ent.","Funcion":fn,"OSINT":fn,"Ubicacion":lugar[0],"Lat":lugar[1],"Lon":lugar[2],"Cuadrante":"Q1","Aethyr":"LIL"})
    geo_map_data.append({"Comandante":id_nodo,"Nombre":nombre,"Faccion":"DERECHA (Control)","Rango":rango,"Lat":lugar[1],"Lon":lugar[2],"Ubicacion":lugar[0],"Legiones":legiones,"Entidades":entidades,"Cuadrante":"Q1","Fuente":"Liber Scientiae"})

# Gobernadores
for g in GOBERNADORES_91:
    id_nodo = f"Gobernador {g['nombre']}"
    raiz = "BEYN_KRIMA" if g["cuadrante"]=="UMBRAL" else "YAMIN_DEXIOS"
    entidades = g["legiones"] * ENTIDADES_POR_LEGION
    comandantes.append({"IdNodo":id_nodo,"Comandante":g["nombre"],"Faccion":"DERECHA (Control)","Raiz":raiz,"Rango":f"Gobernador {g['aethyr']}","Legiones":g["legiones"],"Entidades":entidades,"Legiones_Str":f"{g['legiones']} Legiones / {entidades:,} ent.","Funcion":g["funcion"],"OSINT":g["funcion"],"Ubicacion":g["jurisdiccion"],"Lat":g["lat"],"Lon":g["lon"],"Cuadrante":g["cuadrante"],"Aethyr":g["aethyr"]})
    geo_map_data.append({"Comandante":id_nodo,"Nombre":g["nombre"],"Faccion":"DERECHA (Control)","Rango":f"Gobernador {g['aethyr']}","Lat":g["lat"],"Lon":g["lon"],"Ubicacion":g["jurisdiccion"],"Legiones":g["legiones"],"Entidades":entidades,"Cuadrante":g["cuadrante"],"Fuente":"Liber Scientiae"})

# Vigilantes
comandantes.append({"IdNodo":"Semyaza (Vigilantes)","Comandante":"Semyaza","Faccion":"IZQUIERDA (Caos)","Raiz":"YADA_GINOSKO","Rango":"Comandante","Legiones":200,"Entidades":200*ENTIDADES_POR_LEGION,"Legiones_Str":f"200 Caídos / {200*ENTIDADES_POR_LEGION:,} ent.","Funcion":"Rebelión e Hibridación Genética","OSINT":"Rebelión e Hibridación Genética","Ubicacion":"Monte Hermón","Lat":33.4115,"Lon":35.8566,"Cuadrante":"Q4","Aethyr":"Libro de Enoc"})
geo_map_data.append({"Comandante":"Semyaza (Vigilantes)","Nombre":"Semyaza","Faccion":"IZQUIERDA (Caos)","Rango":"Comandante","Lat":33.4115,"Lon":35.8566,"Ubicacion":"Monte Hermón","Legiones":200,"Entidades":200*ENTIDADES_POR_LEGION,"Cuadrante":"Q4","Fuente":"Libro de Enoc"})

df_geo_map = pd.DataFrame(geo_map_data)
POB_MUNDIAL = 8_100_000_000

mapeo_infraestructura = {
    "BlackRock / Vanguard": "Rey Elemental Iczhihal",
    "Banco de Pagos Internacionales (BIS)": "Rey Elemental Iczhihal",
    "DARPA": "Rey Elemental Bataivah",
    "Palantir Technologies": "Gobernador Zinggenv",
    "CRISPR-Cas9 / Edición Genética": "Rey Asmoday",
    "Biología Sintética / ARNm": "Rey Asmoday",
    "Neuralink": "Rey Bael",
    "OpenAI / Microsoft AI": "Rey Paimon"
}

# --- 7. GENERADOR DEL GRAFO CON RADAR OPERATIVO REAL ---
def generar_mapa_maestro(faccion, c_ling, c_geo, c_bio, textos_raw, activar_radar, limite_v=25):
    G = nx.Graph()
    color_faccion = "#e11d48" if "IZQUIERDA" in faccion else "#2563eb"
    G.add_node(str(faccion), size=65, color=color_faccion, title=f"CENTRO DE MANDO: {faccion}")
    
    if "DERECHA" in faccion:
        raices = {
            "YAMIN_DEXIOS": {"color": "#3b82f6", "desc": "Yamin/Dexios — Autoridad"},
            "BEYN_KRIMA": {"color": "#60a5fa", "desc": "Beyn/Krima — Delimitación"}
        }
    else:
        raices = {
            "SMOL_ARISTEROS": {"color": "#f43f5e", "desc": "Smol/Aristeros — Disolución"},
            "YADA_GINOSKO": {"color": "#fb7185", "desc": "Yada/Ginosko — Indistinción"}
        }
        
    for r_id, info in raices.items():
        G.add_node(r_id, size=45, color=info["color"], title=info["desc"])
        G.add_edge(str(faccion), r_id, weight=4)
        
    comandantes_faccion = [c for c in comandantes if c["Faccion"] == faccion]
    
    # Marcado visible de nodos interceptados por radar
    nodos_interceptados = []
    if activar_radar and comandantes_faccion:
        nodos_interceptados = random.sample(comandantes_faccion, min(4, len(comandantes_faccion)))
        G.add_node("📡 RADAR OSINT ACTIVO", size=50, color="#22c55e", title="Señales activas interceptadas en vivo")
        G.add_edge(str(faccion), "📡 RADAR OSINT ACTIVO", weight=5)

    for cmd in comandantes_faccion:
        id_nodo = cmd["IdNodo"]
        es_interceptado = cmd in nodos_interceptados
        
        color_nodo = "#22c55e" if es_interceptado else ("#3b82f6" if "DERECHA" in faccion else "#e11d48")
        tamano_nodo = 32 if es_interceptado else 14
        
        titulo_hover = f"{'🚨 INTERCEPTADO POR RADAR' if es_interceptado else '👑'} {id_nodo}\n📍 {cmd['Ubicacion']}\n⚔️ {cmd['Legiones_Str']}\n📜 {cmd['Funcion']}"
        G.add_node(id_nodo, size=tamano_nodo, color=color_nodo, title=titulo_hover)
        G.add_edge(cmd["Raiz"], id_nodo, weight=1)
        
        if es_interceptado:
            G.add_edge("📡 RADAR OSINT ACTIVO", id_nodo, weight=3, color="#22c55e")

    # Mapeo Capa 2 y Capa 3
    if not c_geo.empty:
        for _, row in c_geo.iterrows():
            nid = str(row.get('Entidad / Corporación', '')).strip()
            if nid:
                G.add_node(nid, size=24, color="#10b981", title=f"INFRAESTRUCTURA:\n{row.get('Mecanismo de Control','')}")
                if nid in mapeo_infraestructura:
                    target = mapeo_infraestructura[nid]
                    if any(c["IdNodo"] == target for c in comandantes_faccion):
                        G.add_edge(target, nid, weight=2)
                else:
                    G.add_edge(str(faccion), nid, weight=1)

    net = Network(height="600px", width="100%", bgcolor="#0b0f19", font_color="white")
    net.from_nx(G)
    net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=120, spring_strength=0.08)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        ruta_temp = f.name
        net.write_html(ruta_temp)
        
    return ruta_temp, [c["Comandante"] for c in nodos_interceptados]

# --- 8. PLANO SEMÁNTICO RESPONSIVE ---
def generar_plano_semantico(faccion_filtro=None):
    coord_map = {"Q1": (0.5, 0.5), "Q2": (0.5, -0.5), "Q3": (-0.5, 0.5), "Q4": (-0.5, -0.5), "UMBRAL": (0.0, 0.0)}
    pts = []
    
    for g in GOBERNADORES_91:
        if faccion_filtro and faccion_filtro != "DERECHA (Control)": continue
        cx, cy = coord_map.get(g["cuadrante"], (0, 0))
        pts.append({"nombre": g["nombre"], "tipo": f"Gobernador {g['aethyr']}", "cuadrante": g["cuadrante"], "faccion": "DERECHA (Control)", "x": cx + (g["num"]%5 - 2)*0.08, "y": cy + (g["num"]%3 - 1)*0.08, "color": "#38bdf8", "size": 8, "simbolo": "circle"})
        
    for cmd in comandantes:
        if cmd["Faccion"] != "IZQUIERDA (Caos)": continue
        if faccion_filtro and faccion_filtro != "IZQUIERDA (Caos)": continue
        cuad = cmd.get("Cuadrante", "Q4")
        cx, cy = coord_map.get(cuad, (-0.5, -0.5))
        pts.append({"nombre": cmd["Comandante"], "tipo": cmd["Rango"], "cuadrante": cuad, "faccion": "IZQUIERDA (Caos)", "x": cx + (hash(cmd["Comandante"])%5 - 2)*0.08, "y": cy + (hash(cmd["Comandante"])%3 - 1)*0.08, "color": "#f43f5e", "size": 9, "simbolo": "diamond"})

    df_p = pd.DataFrame(pts)
    fig = go.Figure()
    
    # Cuadrantes de fondo
    fig.add_shape(type="rect", x0=0, x1=1, y0=0, y1=1, fillcolor="rgba(29,78,216,0.1)", line=dict(color="#1e293b"))
    fig.add_shape(type="rect", x0=0, x1=1, y0=-1, y1=0, fillcolor="rgba(37,99,235,0.1)", line=dict(color="#1e293b"))
    fig.add_shape(type="rect", x0=-1, x1=0, y0=0, y1=1, fillcolor="rgba(190,18,60,0.1)", line=dict(color="#1e293b"))
    fig.add_shape(type="rect", x0=-1, x1=0, y0=-1, y1=0, fillcolor="rgba(225,29,72,0.12)", line=dict(color="#1e293b"))
    
    # Ejes divisores
    fig.add_shape(type="line", x0=-1.1, x1=1.1, y0=0, y1=0, line=dict(color="#475569", dash="dot"))
    fig.add_shape(type="line", x0=0, x1=0, y0=-1.1, y1=1.1, line=dict(color="#475569", dash="dot"))
    
    if not df_p.empty:
        for fac, grp in df_p.groupby("faccion"):
            fig.add_trace(go.Scatter(
                x=grp["x"], y=grp["y"], mode="markers", name=fac,
                marker=dict(size=grp["size"], color=grp["color"], symbol=grp["simbolo"]),
                text=grp["nombre"],
                hovertemplate="<b>%{text}</b> (%{customdata[0]})<br>Cuadrante: %{customdata[1]}<extra></extra>",
                customdata=grp[["tipo", "cuadrante"]].values
            ))
            
    fig.update_layout(
        plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8",
        xaxis=dict(range=[-1.15, 1.15], showgrid=False, zeroline=False, fixedrange=True),
        yaxis=dict(range=[-1.15, 1.15], showgrid=False, zeroline=False, fixedrange=True),
        margin=dict(l=10, r=10, t=30, b=30),
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

# --- 9. MAPA TERRESTRE RESPONSIVE ---
def generar_mapa_cuadrantes_tierra():
    fig = go.Figure()
    df_g = df_geo_map[df_geo_map["Lat"].notna() & (df_geo_map["Lat"] != 0)]
    
    for faccion, group in df_g.groupby("Faccion"):
        color = "#3b82f6" if "DERECHA" in faccion else "#ef4444"
        fig.add_trace(go.Scattergeo(
            lat=group["Lat"], lon=group["Lon"], mode="markers", name=faccion,
            marker=dict(size=group["Legiones"].apply(lambda x: max(6, min(20, x//8))), color=color, opacity=0.8),
            text=group["Nombre"],
            customdata=group[["Rango", "Ubicacion", "Legiones", "Entidades"]].values,
            hovertemplate="<b>%{text}</b> (%{customdata[0]})<br>Ubicación: %{customdata[1]}<br>Legiones: %{customdata[2]}<br>Entidades: %{customdata[3]:,}<extra></extra>"
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
        margin=dict(l=0, r=0, t=20, b=0),
        height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    return fig

# --- 10. RENDERIZADO DE PESTAÑAS ---
tab_core, tab_geo_d, tab_plano, tab_tierra, tab_ratio, tab_radar, tab_predict, tab_timeline, tab0, tab1, tab2, tab3 = st.tabs([
    "🔄 Enjambre", "🗺️ Geo-Densidad", "🧭 Plano Semántico",
    "🌍 Cuadrantes", "⚖️ Ratio Legiones", "📡 Radar",
    "🎯 Predictivo", "⏱️ Timeline",
    "📖 V0-Textos", "🔮 V1-Esotérico", "🌐 V2-Geo", "👥 Arquetipos"
])

# TAB CORE
with tab_core:
    col1, col2 = st.columns([2, 1])
    with col1:
        faccion_maestra = st.radio("Ala de Jerarquía:", ["DERECHA (Control)", "IZQUIERDA (Caos)"], horizontal=True)
    with col2:
        activar_radar = st.checkbox("📡 Interceptar Radar OSINT", value=False)
        
    c_geo_t = df_geo[df_geo["Facción Alineada"] == faccion_maestra] if not df_geo.empty else pd.DataFrame()
    c_bio_t = df_bio[df_bio["Facción Alineada"] == faccion_maestra] if not df_bio.empty else pd.DataFrame()
    
    ruta_grafo, interceptados = generar_mapa_maestro(faccion_maestra, pd.DataFrame(), c_geo_t, c_bio_t, textos_raw_eso, activar_radar, limite_nodos_texto)
    
    if activar_radar and interceptados:
        st.success(f"🟢 **Señales interceptadas activas en:** {', '.join(interceptados)}")
        
    with open(ruta_grafo, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=620)
    try:
        os.remove(ruta_grafo)
    except Exception:
        pass

# TAB GEO-DENSIDAD
with tab_geo_d:
    st.subheader("🗺️ Mapeo Geo-Densidad")
    df_z = df_geo_map.groupby(["Ubicacion","Lat","Lon","Faccion"]).agg({"Entidades":"sum","Legiones":"sum","Nombre":"count"}).reset_index()
    fig_map = px.scatter_geo(df_z, lat="Lat", lon="Lon", size="Entidades", color="Faccion", hover_name="Ubicacion", projection="natural earth", color_discrete_map={"DERECHA (Control)":"#3b82f6","IZQUIERDA (Caos)":"#ef4444"})
    fig_map.update_geos(showcountries=True, countrycolor="#334155", showland=True, landcolor="#0f172a", showocean=True, oceancolor="#0b0f19")
    fig_map.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8", margin=dict(l=0, r=0, t=10, b=0), height=480, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
    st.plotly_chart(fig_map, use_container_width=True, config=PLOTLY_CONFIG)

# TAB PLANO SEMÁNTICO
with tab_plano:
    st.subheader("🧭 Espacio Semántico")
    filtro_fac = st.selectbox("Filtrar facción:", ["Todas", "DERECHA (Control)", "IZQUIERDA (Caos)"])
    filtro = None if filtro_fac == "Todas" else filtro_fac
    st.plotly_chart(generar_plano_semantico(filtro), use_container_width=True, config=PLOTLY_CONFIG)

# TAB TIERRA
with tab_tierra:
    st.subheader("🌍 Cuadrantes Proyectados en Geografía")
    st.plotly_chart(generar_mapa_cuadrantes_tierra(), use_container_width=True, config=PLOTLY_CONFIG)

# TAB RATIO (CORREGIDO MATEMÁTICAMENTE)
with tab_ratio:
    st.subheader("⚖️ Conteo de Legiones y Ratio por Habitante")
    st.caption(f"Base: 1 legión = {ENTIDADES_POR_LEGION:,} entidades. Población humana mundial: {POB_MUNDIAL:,}")
    
    entidades_izq = df_geo_map[df_geo_map["Faccion"] == "IZQUIERDA (Caos)"]["Entidades"].sum()
    entidades_der = df_geo_map[df_geo_map["Faccion"] == "DERECHA (Control)"]["Entidades"].sum()
    total_ent = entidades_izq + entidades_der
    total_leg = df_geo_map["Legiones"].sum()

    ratio_global = total_ent / POB_MUNDIAL
    humanos_por_entidad = POB_MUNDIAL / total_ent if total_ent > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Legiones totales", f"{total_leg:,}")
    c2.metric("Entidades totales", f"{total_ent:,}")
    c3.metric("Ratio de presencia", f"{ratio_global:.4f} ent./hab.")
    c4.metric("Entidades IZQ / DER", f"{entidades_izq:,} | {entidades_der:,}")
    c5.metric("Distribución demográfica", f"1 ent. cada {round(humanos_por_entidad):,} hab.")

    st.markdown("---")
    fig_tree = px.treemap(
        df_geo_map, path=["Faccion", "Fuente", "Rango"], values="Entidades",
        color="Faccion", color_discrete_map={"IZQUIERDA (Caos)": "#e11d48", "DERECHA (Control)": "#2563eb"}
    )
    fig_tree.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8", margin=dict(l=0, r=0, t=10, b=0), height=450)
    st.plotly_chart(fig_tree, use_container_width=True, config=PLOTLY_CONFIG)

# TAB RADAR
with tab_radar:
    st.subheader("📡 Radar OSINT en Tiempo Real")
    if input_api_key:
        st.caption("🟢 Conectado con NewsAPI personalizada.")
    else:
        st.caption("🟡 Usando fallback público RSS (ingresa tu clave en la barra lateral para mayor precisión).")

    if st.button("🔍 Escanear Noticias Relevantes", type="primary"):
        with st.spinner("Interceptando transmisiones..."):
            muestra = random.sample(comandantes, min(5, len(comandantes)))
            encontrados = 0
            for cmd in muestra:
                noticias = buscar_noticias_entidad(cmd["Funcion"], cmd["Comandante"], NEWSAPI_KEY)
                if noticias:
                    encontrados += 1
                    with st.expander(f"Señal en {cmd['IdNodo']} ({cmd['Funcion']})", expanded=True):
                        for n in noticias[:2]:
                            st.markdown(f"**[{n['fuente']}]** [{n['titulo']}]({n['url']}) — *{n['fecha']}*")
                            st.caption(n['descripcion'][:160] + "...")
            if encontrados == 0:
                st.info("No se hallaron anomalías críticas en este ciclo.")

# TAB PREDICTIVO
with tab_predict:
    st.subheader("🎯 Convergencia Vectorial Capa 2 / Capa 3")
    cp1, cp2 = st.columns(2)
    with cp1:
        vg = st.selectbox("Entidad / Infraestructura:", df_geo['Entidad / Corporación'].dropna().tolist())
    with cp2:
        vb = st.selectbox("Tecnología / Plataforma:", df_bio['Avance / Plataforma'].dropna().tolist())

    if st.button("Evaluar Alineamiento", type="primary"):
        fg = df_geo[df_geo['Entidad / Corporación'] == vg]['Facción Alineada'].values[0] if vg in df_geo['Entidad / Corporación'].values else "Neutral"
        fb = df_bio[df_bio['Avance / Plataforma'] == vb]['Facción Alineada'].values[0] if vb in df_bio['Avance / Plataforma'].values else "Neutral"
        
        if fg == fb:
            st.success(f"⚠️ CONVERGENCIA SISTÉMICA ALTA ({fg}): Ambos vectores canalizan la misma polaridad de influencia.")
        else:
            st.warning(f"⚡ FRICCIÓN ESTRUCTURAL: {vg} ({fg}) opera en oposición táctica a {vb} ({fb}).")

# TAB TIMELINE
with tab_timeline:
    st.subheader("⏱️ Reloj Temporal")
    if 'Inicio' in df_astro.columns and 'Fin' in df_astro.columns:
        fig_tl = px.timeline(df_astro.dropna(subset=['Inicio','Fin']), x_start="Inicio", x_end="Fin", y="Ciclo / Marcador Celeste", color="Facción Alineada", color_discrete_map={"DERECHA (Control)":"#3b82f6","IZQUIERDA (Caos)":"#f43f5e","Ambas / Reloj":"#0ea5e9"})
        fig_tl.update_yaxes(autorange="reversed")
        fig_tl.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8", height=350, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_tl, use_container_width=True, config=PLOTLY_CONFIG)

# TABLAS RAW
with tab0: st.dataframe(df_ling_masivo, use_container_width=True, hide_index=True)
with tab1: st.dataframe(df_eso_base, use_container_width=True, hide_index=True)
with tab2: st.dataframe(df_geo, use_container_width=True, hide_index=True)
with tab3: st.dataframe(df_arquetipos, use_container_width=True, hide_index=True)